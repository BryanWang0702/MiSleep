# -*- coding: UTF-8 -*-
"""Automatic sleep staging with the benchmark LightGBM models.

The packaged ``benchmark_models.pkl`` contains six LightGBM classifiers
(one per channel combo: EEG site x optional EMG x optional ACC), each
combined with a per-recording z-score normalisation, a learned 3-state HMM
and class priors. **Every mouse age and EEG site use the same model file**;
the age / site arguments are kept only for API compatibility.

The pipeline (adapted from the rodent-autostage benchmark):

1. feature extraction on 5 s epochs (STFT band powers + time-domain
   features + EEG-EMG coherence, W = 10 s window at 1 s stride),
2. per-recording z-score normalisation,
3. LightGBM class probabilities,
4. HMM / Viterbi decoding with a softmax temperature,
5. physiologically constrained smoothing (Init -> Wake, REM never after
   Wake, single-epoch flip removal),
6. per-second expansion of the per-epoch states.

Besides the per-second labels, the per-epoch probability of the predicted
state is returned (the *confidence* used by the GUI to mark low-confidence
regions in the hypnogram).
"""

from __future__ import annotations

import copy
from pathlib import Path

import numpy as np

from misleep._compat import resource_dir
from misleep.logger import logger


def _model_dir() -> Path:
    """Return the directory containing the packaged LightGBM models."""
    return resource_dir("misleep.analysis.models")


def model_path(mouse_age="adult", EEG_channel="F") -> Path:
    """Return the path of the packaged benchmark models.

    A single model file serves every mouse age and EEG site, so
    ``mouse_age`` and ``EEG_channel`` are accepted for API compatibility
    only.

    Parameters
    ----------
    mouse_age : str
        Accepted for API compatibility (ignored).
    EEG_channel : str
        Accepted for API compatibility (ignored).

    Returns
    -------
    Path
    """
    return _model_dir() / "benchmark_models.pkl"


def result_constraints(pred_prob):
    """Post-process raw model probabilities into smooth state labels.

    Applies the following constraints:

    1. A REM probability below 0.15 is overridden.
    2. REM directly after Wake is set to NREM.
    3. State 4 (Init) is set to Wake.
    4. A single epoch between two identical states takes that state.

    Parameters
    ----------
    pred_prob : ndarray
        Model output probabilities, shape ``(n_windows, n_classes)``.

    Returns
    -------
    list of int
        Per-window predicted state codes (1-indexed).
    """
    pred_prob = copy.deepcopy(pred_prob)
    pred_label = [each + 1 for each in np.argmax(pred_prob, axis=1)]
    pred_label = [2 if each[1] > 0.15 else pred_label[idx]
                  for idx, each in enumerate(pred_prob)]

    for idx in range(1, len(pred_label) - 1):
        label_ = pred_label[idx]

        if label_ == 4:
            pred_label[idx] = 3
        if label_ == 3 and pred_label[idx + 1] == 2:  # REM after Wake
            pred_label[idx + 1] = 1
        if pred_label[idx - 1] == pred_label[idx + 1] and pred_label[idx] != 3:
            pred_label[idx] = pred_label[idx - 1]

    return pred_label


def auto_stage_gbm(EEG, EMG, label, sf, EEG_channel="F", mouse_age="adult",
                   ACC=None, return_probs=False, temperature=0.1):
    """Auto-stage a recording with the benchmark LightGBM models.

    All mouse ages use the same model; ``mouse_age`` is kept for API
    compatibility. The channel combo (EEG site x EMG x ACC) selects which
    of the six benchmark models is used - ACC requires EMG.

    Parameters
    ----------
    EEG : ndarray
        EEG signal.
    EMG : ndarray or None
        EMG signal (optional; pass ``None`` to run EEG-only).
    label : list
        Reference labels (kept for API compatibility; not used by the model).
    sf : float
        Sampling frequency of the signals.
    EEG_channel : {'F', 'P'}
        EEG electrode site (frontal or parietal). Default is ``'F'``.
    mouse_age : str
        Accepted for API compatibility (ignored - all ages use the same
        model).
    ACC : ndarray or None
        ACC signal (optional; requires ``EMG``).
    return_probs : bool
        Also return the per-epoch confidence (probability of the predicted
        state) as a numpy array.
    temperature : float
        HMM softmax temperature (lower sharpens the transition structure).

    Returns
    -------
    list of int, or (list of int, ndarray) when ``return_probs`` is True.
        Per-second predicted state codes (1 = NREM, 2 = REM, 3 = Wake),
        plus the per-epoch confidence when requested. The prediction may
        be a few seconds shorter than the recording (window drop).
    """
    from misleep.analysis.autostage import benchmark as _bm

    if EEG is None or len(np.asarray(EEG)) / sf < _bm.W + _bm.EPOCH_S:
        raise ValueError(
            "Signal too short for auto staging (need at least "
            f"{int(_bm.W + _bm.EPOCH_S)} s).")
    if ACC is not None and EMG is None:
        raise ValueError("ACC auto-staging requires an EMG channel as well.")

    use_emg = EMG is not None
    use_acc = ACC is not None
    combo = _bm.model_combo(EEG_channel, use_emg, use_acc)

    models = _bm.load_models()
    if combo not in models:
        # ACC without EMG is not part of the model set - fall back to the
        # EEG+EMG (or EEG-only) model.
        if use_acc and use_emg:
            raise ValueError(
                f"No model for combo '{combo}' in the packaged models.")
        combo = _bm.model_combo(EEG_channel, use_emg, False)

    sig_map = {"eeg": EEG, "emg": EMG, "acc": ACC}
    res = _bm.predict_model(models[combo], sig_map, sf,
                            site=EEG_channel, temperature=temperature)

    # Full-length per-second labels (every second gets a label; the first
    # W seconds and the tail take the nearest epoch) + per-epoch confidence
    # (one value per 5 s epoch - small data).
    pred_second = [int(x) for x in res["label_sec"]]
    conf_epoch = np.asarray(res["prob"], dtype=float)
    logger.info(
        "Auto staging finished (combo=%s, %d epochs, %d seconds)",
        combo, len(res["label"]), len(pred_second))

    if return_probs:
        return pred_second, conf_epoch
    return pred_second
