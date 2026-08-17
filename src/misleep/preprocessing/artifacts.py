# -*- coding: UTF-8 -*-
"""Artifact rejection.

The current implementation rejects 5-second epochs whose standard
deviation deviates strongly from the average epoch standard deviation
(:func:`reject_artifact`).
"""

import numpy as np


def z_score(signal):
    """Standardize a signal: ``(x - mean) / std``.

    Parameters
    ----------
    signal : ndarray
        Signal data.

    Returns
    -------
    ndarray
        Z-scored signal.
    """
    lst_mean = np.mean(signal, axis=0)
    lst_std = np.std(signal, axis=0)
    normalized_data = (signal - lst_mean) / lst_std
    return normalized_data


def reject_artifact(signal, sf=None, threshold=2):
    """Reject artifact epochs based on per-epoch standard deviation.

    The signal is split into 5-second epochs; every epoch whose standard
    deviation is ``threshold`` times larger than the mean epoch standard
    deviation is removed, and the remaining samples are concatenated.

    Parameters
    ----------
    signal : ndarray
        Signal data.
    sf : float, optional
        Sampling frequency. When ``None`` the epoch length defaults to
        1/5th of the signal.
    threshold : float
        Relative standard-deviation threshold. Default is 2.

    Returns
    -------
    ndarray
        The cleaned signal (may be shorter than the input).
    """
    signal_z_score = z_score(signal)
    # get epoch data (5 second windows)
    if sf is None:
        sf = signal_z_score.shape[0] / 5
    signal_z_score = [
        signal_z_score[int(each): int(each + 5 * sf)]
        for each in range(0, signal_z_score.shape[0], int(5 * sf))
    ]
    signal_SD_lst = [np.std(each) for each in signal_z_score]
    ave_signal_sd = np.mean(signal_SD_lst)
    artifacts_idx = []

    for each in signal_SD_lst:
        if each / ave_signal_sd >= threshold:
            artifacts_idx.append(0)
        else:
            artifacts_idx.append(1)

    artifacts_idx = np.array(artifacts_idx).astype(bool)
    artifacts_idx = np.repeat(artifacts_idx, int(5 * sf))
    slice_length = artifacts_idx.shape[0] if artifacts_idx.shape[0] < len(signal) else len(signal)
    signal = np.array(signal[:slice_length])[artifacts_idx[:slice_length]]

    return signal
