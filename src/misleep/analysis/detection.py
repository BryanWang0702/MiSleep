# -*- coding: UTF-8 -*-
"""Event detection: slow-wave activity (SWA), sleep spindles, artifacts.

All detectors operate on 1-D signal arrays plus a sampling frequency and
return either a list of detections or a pandas DataFrame (``df=True``).
"""

import numpy as np
import pandas as pd
from scipy.signal import find_peaks

from misleep.preprocessing.filtering import signal_filter
from misleep.preprocessing.spectral import spectrogram
from misleep.utils.annotation import lst2group


def SWA_detection(signal, sf, freq_band=[0.5, 4], amp_threshold=(75,), df=False, start_time_sec=0):
    """Slow-wave activity (SWA) detection.

    The signal is band-pass filtered to ``freq_band``; waves are detected
    from trough to peak using relative amplitude thresholds and validated
    by their instantaneous frequency.

    Parameters
    ----------
    signal : ndarray
        Signal to analyze.
    sf : float
        Sampling frequency.
    freq_band : list of two floats
        Frequency band of the slow wave, e.g. ``[0.5, 4]`` Hz.
    amp_threshold : tuple
        Minimum (and optionally maximum) absolute amplitude of the peaks.
    df : bool
        Whether to return a pandas DataFrame instead of a list.
    start_time_sec : float
        Offset (in seconds) added to all detection times -- useful when
        processing segments of a longer recording.

    Returns
    -------
    list or pandas.DataFrame or None
        Detections (``None`` when nothing was found).
    """
    band_data, _ = signal_filter(signal, sf, btype="bandpass",
                                 low=freq_band[0], high=freq_band[1])

    # Find peaks and zero-crossings
    pos_peak_idx, _ = find_peaks(band_data, amp_threshold)
    neg_peak_idx, _ = find_peaks(-1 * band_data, amp_threshold)
    zero_crossing = np.where(np.diff(np.signbit(band_data), axis=0))[0]

    # Find zero -> neg_peak -> zero -> pos_peak -> zero pattern
    negative_peaks_hold = []
    positive_peaks_hold = []
    zero_crossing_hold = []
    for neg_idx in neg_peak_idx:
        for zero_idx in zero_crossing:
            if zero_idx > neg_idx:
                for pos_idx in pos_peak_idx:
                    if pos_idx > zero_idx and zero_idx not in zero_crossing_hold:
                        if True not in (band_data[zero_idx + 1: pos_idx] <= 0) and \
                                True not in (band_data[neg_idx: zero_idx] >= 0):
                            negative_peaks_hold.append(neg_idx)
                            positive_peaks_hold.append(pos_idx)
                            zero_crossing_hold.append(zero_idx)
                        break
                break

    if negative_peaks_hold == []:
        return None

    # zero before the negative peak
    start_zero_cross_hold = zero_crossing[:-1][np.diff(
        np.searchsorted(negative_peaks_hold, zero_crossing)).astype(bool)]

    if zero_crossing[-1] < positive_peaks_hold[-1]:
        zero_crossing = np.append(zero_crossing, positive_peaks_hold[-1] + 1)
    end_zero_cross_hold = zero_crossing[np.searchsorted(zero_crossing, positive_peaks_hold)]

    df_lst = []
    for idx, start_zero in enumerate(start_zero_cross_hold):
        start_time = start_zero / sf + start_time_sec
        end_time = end_zero_cross_hold[idx] / sf + start_time_sec
        total_duration = end_time - start_time
        frequency = 1 / total_duration
        if frequency > freq_band[1] or frequency < freq_band[0]:
            continue

        middle_cross_time = zero_crossing_hold[idx] / sf + start_time_sec
        time_pos_peak = positive_peaks_hold[idx] / sf + start_time_sec
        val_pos_peak = band_data[positive_peaks_hold[idx]]
        time_neg_peak = negative_peaks_hold[idx] / sf + start_time_sec
        val_neg_peak = band_data[negative_peaks_hold[idx]]

        peak_to_peak = val_pos_peak - val_neg_peak
        slope = peak_to_peak / (time_pos_peak - time_neg_peak)

        df_lst.append([start_time, time_neg_peak, middle_cross_time, time_pos_peak,
                       end_time, total_duration, val_neg_peak, val_pos_peak,
                       peak_to_peak, slope, frequency])

    if df:
        return pd.DataFrame(df_lst, columns=["StartTime", "NegTime", "MiddleTime",
                                             "PosTime", "EndTime", "Duration", "NegPeak",
                                             "PosPeak", "PTP", "Slope", "Frequency"])
    return df_lst


def spindle_detection(signal, sf, freq_band=[10, 15], start_time_sec=0,
                      std_thresh=None, duration_thresh=None):
    """Sleep spindle detection based on spectrogram power.

    The signal's spectrogram power within ``freq_band`` is computed; a
    spindle is defined as a period where the power exceeds
    ``mean + std_thresh * std`` (for detection) and
    ``mean + duration_thresh * std`` (for duration) and lasts at least
    0.5 seconds.

    Parameters
    ----------
    signal : ndarray
        Signal to analyze.
    sf : float
        Sampling frequency.
    freq_band : list of two floats
        Frequency band of the spindle, e.g. ``[10, 15]`` Hz.
    start_time_sec : float
        Offset added to the detection times.
    std_thresh : float, optional
        Std multiplier for the detection threshold (default 2).
    duration_thresh : float, optional
        Std multiplier for the duration threshold (default 1.5).

    Returns
    -------
    list or None
        List of ``[start, end]`` (in seconds) spindle detections.
    """
    if std_thresh is None:
        std_thresh = 2
    if duration_thresh is None:
        duration_thresh = 1.5

    f, t, Sxx = spectrogram(signal, sf, band=freq_band, step=0.2, win_sec=2, norm=False)

    # Summed power over the band, then squared
    Sxx = np.sum(Sxx, axis=0)
    Sxx_squared = Sxx ** 2

    Sxx = Sxx_squared
    Sxx_mean = np.mean(Sxx)
    Sxx_std = np.std(Sxx)
    spindle_threshold = std_thresh * Sxx_std + Sxx_mean
    duration_threshold = duration_thresh * Sxx_std + Sxx_mean

    Sxx_peaks_idx, _ = find_peaks(Sxx, (spindle_threshold))
    if Sxx_peaks_idx.shape == (0,):
        return None

    # Find duration groups
    duration_group = lst2group([[idx, each] for idx, each in enumerate(Sxx > duration_threshold)])
    start_time = []
    end_time = []
    for each in duration_group:
        if each[0] != 0 and each[2]:
            if each[1] < len(t) and each[2]:
                start_time.append(t[each[0]])
                end_time.append(t[each[1]])

    start_time = np.array(start_time)
    end_time = np.array(end_time)

    if start_time.shape != end_time.shape:
        return None
    if start_time.shape == (0,):
        return None

    start_time = start_time + start_time_sec
    end_time = end_time + start_time_sec

    return [[each, end_time[idx]] for idx, each in enumerate(start_time)
            if end_time[idx] - each >= 0.5]


def artifact_detection(signal):
    """Artifact detection (placeholder).

    Parameters
    ----------
    signal : ndarray
        Signal to analyze.

    Returns
    -------
    None
    """
    return None
