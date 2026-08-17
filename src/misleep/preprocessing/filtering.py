# -*- coding: UTF-8 -*-
"""Signal filtering.

Currently provides a Butterworth zero-phase filter through
:func:`signal_filter` and mains (power-line) noise removal through
:func:`filter_power_line_noise`.
"""

import numpy as np
from scipy import signal


def signal_filter(data, sf=256.0, btype="lowpass", low=0.5, high=30.0):
    """Filter a signal with a zero-phase Butterworth filter.

    Parameters
    ----------
    data : ndarray
        1-D array, the signal to filter.
    sf : float
        Sampling frequency of the signal. Default is 256.
    btype : {'lowpass', 'highpass', 'bandpass', 'bandstop'}, optional
        The type of filter. Default is ``'lowpass'``.
    low : float
        Lower cutoff frequency (Hz), used by ``'highpass'``, ``'bandpass'``
        and ``'bandstop'``.
    high : float
        Higher cutoff frequency (Hz), used by ``'lowpass'``, ``'bandpass'``
        and ``'bandstop'``.

    Returns
    -------
    filtered_data : ndarray
        The filtered signal.
    fname : str
        A short name describing the filter, e.g. ``'bandpass_0.5_30'``.
    """
    if not isinstance(sf, (int, float)):
        raise TypeError(f"Sample frequency should be a float, got {type(sf)}")
    if not isinstance(low, (int, float)):
        raise TypeError(f"Low threshold should be a float, got {type(low)}")
    if not isinstance(high, (int, float)):
        raise TypeError(f"High threshold should be a float, got {type(high)}")

    if btype == "lowpass":
        fnorm = high / (0.5 * sf)
        fname = f"{btype}_{high}"
    elif btype == "highpass":
        fnorm = low / (0.5 * sf)
        fname = f"{btype}_{low}"
    elif btype in ("bandpass", "bandstop"):
        fnorm = np.divide([low, high], 0.5 * sf)
        fname = f"{btype}_{low}_{high}"
    else:
        raise ValueError(
            f"'{btype}' is an invalid type for filter, you can only choose "
            f"'lowpass', 'highpass', 'bandpass' or 'bandstop'")

    b, a = signal.iirfilter(N=3, Wn=fnorm, btype=btype, analog=False,
                            output="ba", ftype="butter", fs=None)
    filtered_data = signal.filtfilt(b=b, a=a, x=data)

    return filtered_data, fname


def filter_power_line_noise(data, sf, noise_band="50-100-150"):
    """Remove mains (power-line) noise with band-stop filters.

    Parameters
    ----------
    data : ndarray
        Signal to filter.
    sf : float
        Sampling frequency.
    noise_band : {'50-100-150', '60-120-180'}, optional
        Mains frequency harmonics to remove. ``'60-120-180'`` is not yet
        implemented.

    Returns
    -------
    ndarray
        The filtered signal.
    """
    filter_band = []
    if noise_band == "50-100-150" and sf > 306:
        filter_band = [[47, 53], [97, 103], [147, 153]]
    elif noise_band == "50-100-150" and sf > 206:
        filter_band = [[47, 53], [97, 103]]
    elif sf > 106:
        filter_band = [[47, 53]]
    for each in filter_band:
        data, _ = signal_filter(data, sf, btype="bandstop", low=each[0], high=each[1])

    return data
