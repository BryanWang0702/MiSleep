# -*- coding: UTF-8 -*-
"""Feature extraction for automatic sleep staging.

Implements the window-based time- and frequency-domain features used by
the LightGBM auto-staging model (EEG and EMG).
"""

from math import floor

import numpy as np
import pandas as pd
from scipy import stats

from misleep.preprocessing.spectral import spectrogram, band_power
from misleep.utils.entropy import hjorth_params, num_zerocross, perm_entropy


def split_window_data(data, sf, state, window_length=20, stride_length=5):
    """Split a signal into sliding windows.

    Parameters
    ----------
    data : ndarray
        Signal to split.
    sf : float
        Sampling frequency.
    state : int
        State code attached to every window (used as the label).
    window_length : int
        Window length in seconds.
    stride_length : int
        Stride in seconds.

    Returns
    -------
    list
        List of ``[window_array, state]`` pairs. Empty when the signal is
        shorter than the window.
    """
    if data.shape[0] / sf < window_length:
        return []

    window_data = []
    data_sec_length = floor(data.shape[0] / sf)
    for i in range(0, data_sec_length - stride_length, stride_length):
        window = data[int(i * sf): int((i + window_length) * sf)]
        window_data.append([window, state])

    return window_data


def delta_theta_ratio_theta(data, sf):
    """Delta/theta ratio and theta power from the first 5 seconds.

    Parameters
    ----------
    data : ndarray
        Windowed signal (20 s).
    sf : float
        Sampling frequency.

    Returns
    -------
    (ratio, theta_power) : tuple of float
    """
    freq, t, Sxx = spectrogram(data, sf, win_sec=1)
    band_second = np.where(t < 5)
    psd = np.sum(np.array([each[band_second] for each in Sxx]), axis=1)
    band_power_dict = band_power(psd, freq, bands=[[0.5, 4, "delta"], [5, 9, "theta"]], relative=True)
    return band_power_dict["delta"] / band_power_dict["theta"], band_power_dict["theta"]


def self_zscore(feature, quantile=0.95):
    """Quantile-clipped z-score normalization of a feature array."""
    upper_quantile = np.quantile(feature, quantile)
    feature = [each if each < upper_quantile else upper_quantile for each in feature]
    return (feature - np.mean(feature)) / np.std(feature)


def get_data_features(data, sf, data_format="EEG"):
    """Extract the auto-staging feature set from windowed data.

    Parameters
    ----------
    data : list
        List of ``[window_array, label]`` pairs (see :func:`split_window_data`).
    sf : float
        Sampling frequency.
    data_format : {'EEG', 'EMG'}
        Which channel type the windows come from. EEG additionally gets
        skewness, kurtosis, delta/theta ratio and theta power.

    Returns
    -------
    pandas.DataFrame
        Feature table with a ``label`` column.
    """
    window_feature_df = pd.DataFrame()
    window_feature_df["label"] = [each[1] for each in data]

    # ---- Time-domain features, both EEG and EMG ----
    data_std = np.array([np.std(each[0][:int(5 * sf)]) for each in data])
    window_feature_df[f"{data_format}_std_zscore"] = self_zscore(data_std)

    zerocross_rate = [num_zerocross(each[0][:int(5 * sf)]) / (5 * sf) for each in data]
    window_feature_df[f"{data_format}_zerocross_rate"] = \
        (zerocross_rate - np.mean(zerocross_rate)) / np.std(zerocross_rate)

    hjorth = [hjorth_params(each[0][:int(5 * sf)]) for each in data]
    hjorth_M = [each[0] for each in hjorth]
    hjorth_C = [each[1] for each in hjorth]
    window_feature_df[f"{data_format}_Hjorth_M"] = self_zscore(hjorth_M)
    window_feature_df[f"{data_format}_Hjorth_C"] = self_zscore(hjorth_C)

    perm_entropy_ = [perm_entropy(each[0][:int(5 * sf)]) for each in data]
    window_feature_df[f"{data_format}_perm_entropy"] = self_zscore(perm_entropy_)

    # ---- EEG-only features ----
    if data_format.startswith("EEG"):
        data_skewness = np.array([stats.skew(each[0][:int(5 * sf)]) for each in data])
        data_kurtosis = np.array([stats.kurtosis(each[0][:int(5 * sf)]) for each in data])
        window_feature_df[f"{data_format}_skewness_zscore"] = self_zscore(data_skewness)
        window_feature_df[f"{data_format}_kurtosis_zscore"] = self_zscore(data_kurtosis)

        delta_theta = [delta_theta_ratio_theta(each[0], sf) for each in data]
        delta_theta_ratio = [each[0] for each in delta_theta]
        theta = [each[1] for each in delta_theta]
        window_feature_df[f"{data_format}_delta_theta_ratio"] = self_zscore(delta_theta_ratio)
        window_feature_df[f"{data_format}_theta"] = self_zscore(theta)

    return window_feature_df
