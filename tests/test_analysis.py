# -*- coding: UTF-8 -*-
"""Tests for the analysis module: detection, features and auto staging."""

import numpy as np
import pytest

from misleep.analysis.auto_stage import auto_stage_gbm, model_path, result_constraints
from misleep.analysis.detection import SWA_detection, spindle_detection
from misleep.analysis.features import get_data_features, split_window_data

from helpers import make_emg, make_signal


def test_swa_detection_on_synthetic():
    sf = 256.0
    t = np.arange(sf * 60) / sf
    # ~1 Hz slow wave with a large amplitude
    signal = 80.0 * np.sin(2 * np.pi * 1.0 * t)
    detections = SWA_detection(signal, sf, freq_band=[0.5, 4], amp_threshold=(40,))
    assert detections is not None
    assert len(detections) > 0
    assert len(detections[0]) == 11  # full feature row


def test_swa_detection_df(midata):
    detections = SWA_detection(midata.signals[0], midata.sf[0], df=True)
    if detections is not None:
        assert "StartTime" in detections.columns
        assert "Frequency" in detections.columns


def test_spindle_detection_on_synthetic():
    sf = 256.0
    t = np.arange(sf * 60) / sf
    # 12 Hz spindle burst in the middle
    signal = 0.5 * np.random.default_rng(0).standard_normal(t.size)
    burst = np.exp(-((t - 30) ** 2) / 8) * np.sin(2 * np.pi * 12 * t) * 50
    signal = signal + burst
    detections = spindle_detection(signal, sf, freq_band=[10, 15], std_thresh=2, duration_thresh=1.5)
    if detections is not None:
        assert all(d[1] > d[0] for d in detections)


def test_split_window_data():
    data = np.zeros(256 * 100)
    windows = split_window_data(data, 256, state=4, window_length=20, stride_length=5)
    assert len(windows) > 0
    assert windows[0][1] == 4
    assert windows[0][0].shape == (256 * 20,)


def test_split_window_data_too_short():
    assert split_window_data(np.zeros(256 * 10), 256, state=4, window_length=20) == []


def test_get_data_features():
    windows = split_window_data(make_signal(), 256, state=1)
    features = get_data_features(windows, 256, data_format="EEG")
    assert "label" in features.columns
    assert "EEG_std_zscore" in features.columns
    assert "EEG_delta_theta_ratio" in features.columns
    assert features.shape[0] == len(windows)

    emg_features = get_data_features(split_window_data(make_emg(), 256, state=1), 256, data_format="EMG")
    assert "EMG_std_zscore" in emg_features.columns
    assert "EMG_delta_theta_ratio" not in emg_features.columns


def test_result_constraints():
    probs = np.array([
        [0.9, 0.05, 0.05],
        [0.1, 0.8, 0.1],   # REM
        [0.1, 0.1, 0.8],   # Wake
        [0.1, 0.9, 0.0],   # REM after Wake -> set to NREM
    ])
    labels = result_constraints(probs)
    assert labels[0] == 1
    assert labels[1] == 2  # REM
    assert labels[2] == 3  # Wake
    assert labels[3] == 1  # REM after Wake constraint
    assert len(labels) == 4


def test_result_constraints_rem_threshold():
    # REM probability > 0.15 forces REM even when another class has argmax
    probs = np.array([
        [0.3, 0.2, 0.5],  # argmax Wake, but REM prob > 0.15 -> REM
    ])
    labels = result_constraints(probs)
    assert labels[0] == 2


def test_model_path():
    p = model_path(mouse_age="adult", EEG_channel="F")
    assert p.name == "adult_EEG_F_lightgbm.pkl"
    assert p.exists()


def test_auto_stage_gbm():
    sf = 256.0
    eeg = make_signal(sf=sf, duration=100, seed=2)
    emg = make_emg(sf=sf, duration=100, seed=3)
    pred = auto_stage_gbm(EEG=eeg, EMG=emg, label=[4] * 100, sf=sf)
    assert isinstance(pred, list)
    assert len(pred) > 0
    assert all(p in (1, 2, 3) for p in pred)


def test_auto_stage_gbm_too_short():
    with pytest.raises(ValueError):
        auto_stage_gbm(EEG=np.zeros(256 * 5), EMG=np.zeros(256 * 5), label=[], sf=256)
