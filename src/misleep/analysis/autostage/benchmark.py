# -*- coding: UTF-8 -*-
"""Benchmark auto-staging pipeline (feature extraction + HMM prediction).

The packaged ``benchmark_models.pkl`` holds six LightGBM models, one per
channel combo:

    eegf, eegp, eegf_emg, eegp_emg, eegf_emg_acc, eegp_emg_acc

``eegf``/``eegp`` refer to the EEG electrode site (frontal / parietal),
``_emg`` adds the EMG channel and ``_acc`` adds ACC. There is no
ACC-without-EMG model, so ACC requires EMG.

Each model stores the per-recording z-score normalisation done at predict
time, the learned HMM transition matrix and class priors, and the model's
expected feature names.

Prediction returns, per 5 s epoch, the state (1 = NREM, 2 = REM,
3 = Wake) together with the probability of the predicted state - the
*confidence* used by the GUI to mark low-confidence regions in the
hypnogram.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np

from misleep._compat import resource_dir
from misleep.analysis.autostage.features import (
    extract_fast,
    filter_channels,
)
from misleep.analysis.autostage.hmm import (
    forward_backward,
    probs_to_emission,
    viterbi,
)
from misleep.analysis.autostage.model import predict_lgbm
from misleep.analysis.autostage.postprocess import smooth_constraints

EPOCH_S = 5
W = 10.0
STRIDE = 1.0

#: model dict keys -> channel combo names
COMBO_BASE = {"F": "eegf", "P": "eegp"}


def models_path() -> Path:
    """Return the path of the packaged benchmark models file."""
    return resource_dir("misleep.analysis.models") / "benchmark_models.pkl"


@lru_cache(maxsize=4)
def load_models(path=None):
    """Load the six channel-combo benchmark models (cached)."""
    import joblib

    path = Path(path) if path else models_path()
    if not path.exists():
        raise FileNotFoundError(
            f"Model file not found: {path}. Make sure the package data is "
            f"installed (pip install misleep).")
    return joblib.load(path)


def model_combo(site="F", use_emg=False, use_acc=False):
    """Return the benchmark model key for the given channel configuration."""
    base = COMBO_BASE.get(str(site).upper(), "eegf")
    combo = base
    if use_emg:
        combo += "_emg"
    if use_acc:
        combo += "_acc"
    return combo


def extract_recording(sig_map, sf, site="F", W=W, stride=STRIDE):
    """Extract per-epoch (5 s) features from the selected channels.

    Parameters
    ----------
    sig_map : dict
        ``{'eeg': array, 'emg': array | None, 'acc': array | None}``.
    sf : float
        Sampling frequency (same for every channel).
    site : {'F', 'P'}
        EEG electrode site - decides the ``eegf`` / ``eegp`` (and
        ``cohf`` / ``cohp``) feature prefixes.

    Returns
    -------
    dict with ``X`` (epochs, n_feat), ``feature_names``, ``seconds``.
    """
    if sig_map.get("eeg") is None:
        raise ValueError("An EEG channel is required for auto staging.")
    renamed = {}
    if sig_map.get("eeg") is not None:
        renamed["EEG_F" if str(site).upper() == "F" else "EEG_P"] = \
            np.asarray(sig_map["eeg"], dtype=np.float32)
    if sig_map.get("emg") is not None:
        renamed["EMG"] = np.asarray(sig_map["emg"], dtype=np.float32)
    if sig_map.get("acc") is not None:
        renamed["ACC"] = np.asarray(sig_map["acc"], dtype=np.float32)

    filtered = filter_channels(renamed, sf)
    r = extract_fast(filtered, sf, W=W, stride=stride, return_seconds=True)
    X_ps = r["X"]  # per-second features
    secs = r["seconds"]

    # per-second -> per-epoch (5 s mean)
    n_epochs = X_ps.shape[0] // EPOCH_S
    X = X_ps[: n_epochs * EPOCH_S].reshape(n_epochs, EPOCH_S, X_ps.shape[1]).mean(axis=1)

    return {"X": X, "feature_names": r["feature_names"],
            "seconds": secs[: n_epochs * EPOCH_S].reshape(n_epochs, EPOCH_S).mean(axis=1)}


def predict_model(model, sig_map, sf, site="F", temperature=0.3):
    """Predict a recording with a single benchmark model.

    The predictions are aligned to the **full recording** (1 value per
    second): the first ``W`` seconds (window warm-up) take the first
    epoch's label/confidence and the trailing remainder takes the last
    epoch's values, so every second of the recording gets a label.

    Returns a dict with:
        label      : per-epoch (5 s) states (1/2/3)
        prob       : per-epoch probability (confidence) of the predicted state
        probs      : (T, 3) raw class probabilities (pre-HMM)
        label_sec  : per-second states, full recording length
        conf_sec   : per-second confidence, full recording length
    """
    r = extract_recording(sig_map, sf, site=site)
    if r["X"].shape[0] == 0:
        raise ValueError("Signal too short for auto staging.")

    names = r["feature_names"]
    idx = [names.index(n) for n in model["feature_names"]]
    X = r["X"][:, idx].astype(np.float64)

    # per-recording z-score (unsupervised, robust to lab/rig gain)
    mu = X.mean(axis=0)
    std = X.std(axis=0)
    std[std < 1e-8] = 1.0
    Xn = (X - mu) / std

    probs = predict_lgbm(model["model_dict"], Xn)
    probs = np.clip(probs, 1e-9, 1.0)

    # HMM decode
    logp = np.log(probs) / temperature
    p_norm = np.exp(logp - logp.max(1, keepdims=True))
    emission = probs_to_emission(p_norm, model["priors"])
    emission_log = np.log(np.maximum(emission, 1e-9))
    logA = np.log(np.maximum(model["hmm_A"], 1e-9))
    label_epoch = viterbi(emission_log, model["hmm_pi"], logA)
    label_epoch = np.asarray(smooth_constraints(list(label_epoch)), dtype=int)

    # per-epoch confidence of the *final* (post-HMM) decision: the
    # forward-backward posterior of the state chosen by the Viterbi path.
    # This is the HMM-informed confidence, not the raw classifier output.
    classes = model["model_dict"].get("classes_", [1, 2, 3])
    col = {c: i for i, c in enumerate(classes)}
    posterior = forward_backward(emission_log, model["hmm_pi"], logA)
    prob_epoch = np.array([posterior[t, col[label_epoch[t]]]
                           for t in range(len(label_epoch))])

    # per-second labels covering the whole recording: the first W seconds
    # (window warm-up) and the trailing remainder take the nearest epoch,
    # so every second of the recording gets a label.
    n_total = int(len(sig_map["eeg"]) / sf)
    pred_second = np.repeat(label_epoch, EPOCH_S)
    w_head = int(W)
    if len(pred_second) < n_total:
        head = min(w_head, n_total)
        tail = max(0, n_total - head - len(pred_second))
        pred_second = np.concatenate([
            np.full(head, int(label_epoch[0])), pred_second,
            np.full(tail, int(label_epoch[-1]))])[:n_total]

    out = {"label": label_epoch, "prob": prob_epoch, "probs": probs,
           "label_sec": pred_second}
    return out
