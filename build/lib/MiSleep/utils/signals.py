# -*- coding: UTF-8 -*-
"""
@Project: misleep
@File: signals.py
@Author: Xueqiang Wang
@Date: 2024/2/29
@Description:  
"""
import numpy as np
from scipy import signal


def signal_filter(data, sf=256., btype='lowpass', low=0.5, high=30.):
    """
    Filter the signal data, use butter filter in scipy

    Parameters
    ----------
    data : ndarray
        1D array. Signal data need to be filtered.
    sf : float
        Sampling frequency of signal data. Default is 305.
    btype : {'lowpass', 'highpass', 'bandpass'}, optional
        The type of filter. Default is 'lowpass'.
    low : float
        Higher than this frequency can pass, used in 'highpass' and 'bandpass'
        filter. Default is 0.5.
    high : float
        Lower than this frequency can pass, used in 'lowpass' and 'bandpass'
        filter. Default is 30.

    Returns
    ----------
    filtered_data : 1D-array
        Filtered data of signal data using butter filter
    fname : str

    """
    if not isinstance(sf, (int, float)):
        raise TypeError(f"Sample frequency should be a float, got {type(sf)}")

    if not isinstance(low, (int, float)):
        raise TypeError(f"Low threshold should be a float, got {type(sf)}")

    if not isinstance(high, (int, float)):
        raise TypeError(f"high threshold should be a float, got {type(sf)}")

    if btype == 'lowpass':
        fnorm = high / (.5 * sf)
        fname = f"{btype}_{high}"
    elif btype == 'highpass':
        fnorm = low / (.5 * sf)
        fname = f"{btype}_{low}"
    elif btype == 'bandpass':
        fnorm = np.divide([low, high], .5 * sf)
        fname = f"{btype}_{low}_{high}"
    elif btype == 'bandstop':
        fnorm = np.divide([low, high], .5 * sf)
        fname = f"{btype}_{low}_{high}"
    else:
        raise ValueError("'%s' is an invalid type for filter, "
                         "you can only choose 'lowpass', 'highpass', 'bandpass' or 'bandstop'"
                         % btype)

    # Use irrfilter of scipy.signal to construct a filter
    b, a = signal.iirfilter(N=3, Wn=fnorm, btype=btype, analog=False,
                            output='ba', ftype='butter', fs=None)

    filtered_data = signal.filtfilt(b=b, a=a, x=data)

    return filtered_data, fname


