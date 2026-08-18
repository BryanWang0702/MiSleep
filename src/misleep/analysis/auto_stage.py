# -*- coding: UTF-8 -*-
"""Automatic sleep staging with a LightGBM classifier.

The model is trained on 20-second windows (stride 5 s) of EEG and EMG
features; every window label is then expanded back to per-second labels.
"""

import copy
import warnings
from importlib.resources import files
from pathlib import Path

import numpy as np

from misleep.analysis.features import get_data_features, split_window_data
from misleep.logger import logger


def _model_dir() -> Path:
    """Return the directory containing the packaged LightGBM models."""
    ref = files("misleep.analysis.models")
    return Path(str(ref)) if ref.is_dir() else ref


def model_path(mouse_age="adult", EEG_channel="F") -> Path:
    """Return the path of a packaged LightGBM model file.

    Parameters
    ----------
    mouse_age : {'adult', 'ado', 'P30'}
        Age category of the model.
    EEG_channel : {'F', 'P'}
        EEG electrode site (frontal or parietal).

    Returns
    -------
    Path
    """
    return _model_dir() / f"{mouse_age}_EEG_{EEG_channel}_lightgbm.pkl"


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


def auto_stage_gbm(EEG, EMG, label, sf, EEG_channel="F", mouse_age="adult"):
    """Auto-stage an EEG/EMG recording with the LightGBM model.

    Parameters
    ----------
    EEG : ndarray
        EEG signal.
    EMG : ndarray
        EMG signal.
    label : list
        Reference labels (kept for API compatibility; not used by the model).
    sf : float
        Sampling frequency of both signals.
    EEG_channel : {'F', 'P'}
        EEG electrode site (frontal or parietal). Default is ``'F'``.
    mouse_age : {'adult', 'ado', 'P30'}
        Model age category: adult > P56, ``ado`` is P30~P56, ``P30`` is < P30.

    Returns
    -------
    list of int
        Per-second predicted state codes (1 = NREM, 2 = REM, 3 = Wake).
        May be slightly shorter than the input for the last few seconds.
    """
    try:
        import joblib
    except ImportError as e:  # pragma: no cover
        raise ImportError(
            "Auto staging requires the 'joblib' package. "
            "Install it with: pip install joblib") from e

    EEG_windows = split_window_data(EEG, sf, state=4)
    EMG_windows = split_window_data(EMG, sf, state=4)
    if not EEG_windows or not EMG_windows:
        raise ValueError("Signals are too short for auto staging (need >= 20 s).")

    window_feature_df = get_data_features(EEG_windows, sf, data_format="EEG")
    emg_feature_df = get_data_features(EMG_windows, sf, data_format="EMG")
    # Combine and keep only feature columns (drop 'label')
    window_feature_df = window_feature_df.join(emg_feature_df, lsuffix="_eeg", rsuffix="_emg")
    window_feature_df = window_feature_df.filter(like="E")

    model_file = model_path(mouse_age=mouse_age, EEG_channel=EEG_channel)
    if not model_file.exists():
        raise FileNotFoundError(
            f"Model file not found: {model_file}. "
            f"Make sure the 'misleep' package data is installed "
            f"(pip install misleep) or provide the model manually.")

    # The bundled LightGBM estimators were trained with scikit-learn 1.3.2.
    # Their LabelEncoder is only retained as fitted metadata and is not used
    # by predict_proba(), but newer sklearn versions otherwise print a long
    # compatibility warning on every run.  Limit the suppression narrowly to
    # that known packaged object; all other model-loading warnings remain.
    try:
        from sklearn.exceptions import InconsistentVersionWarning
    except ImportError:  # pragma: no cover - sklearn is a LightGBM dependency
        InconsistentVersionWarning = Warning
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="Setting the shape on a NumPy array has been deprecated.*",
            category=DeprecationWarning,
            module=r"joblib\.numpy_pickle",
        )
        warnings.filterwarnings(
            "ignore",
            message="Trying to unpickle estimator LabelEncoder from version 1.3.2.*",
            category=InconsistentVersionWarning,
        )
        gbm_model = joblib.load(model_file)

    pred_prob = gbm_model.predict_proba(window_feature_df,
                                        num_iteration=gbm_model.best_iteration_)
    pred_label = result_constraints(pred_prob)
    pred_label = [item for each in pred_label for item in [each] * 5]
    logger.info("Auto staging finished (%d windows, %d seconds)",
                len(pred_prob), len(pred_label))
    return pred_label
