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
from copy import deepcopy
from misleep.io.base import MiData
from misleep.utils.annotation import lst2group


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
    try:
        b, a = signal.iirfilter(N=3, Wn=fnorm, btype=btype, analog=False,
                                output='ba', ftype='butter', fs=None)
    except ValueError as e:
        raise ValueError(e)

    filtered_data = signal.filtfilt(b=b, a=a, x=data)

    return filtered_data, fname


def crop_state_data(midata, mianno):
    """Crop the data with annotation into different state data, typically seperate the data into NREM data, REM data, Wake and Init data
    Apply this to every channels
    """
    # Get the sleep state data
    sleep_state = deepcopy(mianno.sleep_state)
    sleep_state = lst2group([[idx, each] for idx, each in enumerate(sleep_state)])
    signals = deepcopy(midata.signals)
    NREM_signals = []
    REM_signals = []
    Wake_signals = []
    Init_signals = []

    for idx, signal in enumerate(signals):
        sf = midata.sf[idx]

        NREM_data = [signal[int(each[0]*sf): int(each[1]*sf)] 
                        for each in sleep_state if each[2] == 1]
        NREM_data = np.array([element for sublist in NREM_data for element in sublist])
        NREM_signals.append(NREM_data)

        REM_data = [signal[int(each[0]*sf): int(each[1]*sf)] 
                        for each in sleep_state if each[2] == 2]
        REM_data = np.array([element for sublist in REM_data for element in sublist])
        REM_signals.append(REM_data)

        Wake_data = [signal[int(each[0]*sf): int(each[1]*sf)] 
                        for each in sleep_state if each[2] == 3]
        Wake_data = np.array([element for sublist in Wake_data for element in sublist])
        Wake_signals.append(Wake_data)
        
        Init_data = [signal[int(each[0]*sf): int(each[1]*sf)] 
                        for each in sleep_state if each[2] == 4]
        Init_data = np.array([element for sublist in Init_data for element in sublist])
        Init_signals.append(Init_data)

    NREM_data = MiData(signals=NREM_signals, channels=midata.channels, sf=midata.sf, time=midata.time, describe='NREM cropped data')
    REM_data = MiData(signals=REM_signals, channels=midata.channels, sf=midata.sf, time=midata.time, describe='REM cropped data')
    Wake_data = MiData(signals=Wake_signals, channels=midata.channels, sf=midata.sf, time=midata.time, describe='Wake cropped data')
    Init_data = MiData(signals=Init_signals, channels=midata.channels, sf=midata.sf, time=midata.time, describe='Init cropped data')

    return NREM_data, REM_data, Wake_data, Init_data


