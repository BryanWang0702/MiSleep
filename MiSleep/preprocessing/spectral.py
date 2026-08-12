# -*- coding: UTF-8 -*-
"""
@Project: misleep
@File: spectral.py
@Author: Xueqiang Wang
@Date: 2024/3/4
@Description:  Spectrum, time-frequency (spectrogram) analysis
"""
import numpy as np
from scipy.signal import welch, stft
from scipy.integrate import simps
from scipy.ndimage import gaussian_filter1d

from misleep.utils.signals import signal_filter


def spectrum(signal, sf, band=None, relative=True, win_sec=1, nfft=None, gaussian_sigma=None):
    """
    Calculate the Welch band power
    Parameters
    ----------
    signal : np.array like
    sf : float
        sample frequency
    band : list, optional
        List of frequency band of interests. Default is [0.5, 30]
    relative : bool
        Whether calculate the relative power of each frequency point
    win_sec : int
        The length of sliding window in fft calculation
    nfft : int, optional
        The number of fft points
    gaussian_sigma : float, optional
        The sigma for gaussian filter
    Returns
    -------
    freq : list
    psd : list
    """
    if not isinstance(signal, np.ndarray):
        raise TypeError(f"'signal' should be np.array like")
    if not isinstance(sf, (int, float)):
        raise TypeError(
            f"'sf' should be an integer or float "
            f"which stands for sample frequency, got {type(sf)}"
        )

    if not isinstance(relative, bool):
        raise TypeError(f"'relative' should be a boolean")

    if band is None:
        band = [0.5, 30]
    if not isinstance(band, list):
        raise TypeError(
            f"'band' should be a list of tuple(s)," f"e.g. [0.5, 4], got {type(band)}"
        )

    signal, _ = signal_filter(
        data=signal, sf=sf, btype="bandpass", low=band[0], high=band[1]
    )

    freq, psd = welch(signal, sf, nperseg=int(sf * win_sec), nfft=nfft, scaling="density")
    freq = np.array([round(each, 2) for each in freq])
    psd = gaussian_filter1d(psd, sigma=gaussian_sigma) if gaussian_sigma is not None else psd

    idx_freq = np.logical_and(freq >= band[0], freq <= band[1])
    freq = freq[idx_freq]
    psd = psd[idx_freq]

    # dx is like the frequency resolution
    total_power = simps(psd, dx=freq[1] - freq[0])
    if relative:
        psd /= total_power

    return freq, psd


def spectrogram(signal, sf, band=None, step=0.2, win_sec=2, norm=False, nfft=None):
    """
    Calculate the spectrogram with scipy.signal.stft
    Parameters
    ----------
    signal : ndarray
        1D array
    sf : int or float
        sample frequency
    band : List
        Frequency band of interests. Default is [0.5, 30]
    step : float
        Step in seconds for the STFT
    win_sec : int
        Window size in seconds for stft
    norm : bool
        Whether normalize the power between frequencies in one time point

    Returns
    -------
    f : ndarray
    t : ndarray
    Sxx : ndarray

    Notes
    -----
    https://github.com/raphaelvallat/yasa/blob/master/yasa/spectral.py
    """

    if not isinstance(signal, np.ndarray):
        raise TypeError(f"'signal' should be np.array like")
    if not isinstance(sf, (int, float)):
        raise TypeError(
            f"'sf' should be an integer or float "
            f"which stands for sample frequency, got {type(sf)}"
        )

    if step > win_sec:
        raise ValueError(f"'step' ({step}) should smaller than 'win_sec' ({win_sec})")
    step = 1 / sf if step <= 0 else step

    if not isinstance(norm, bool):
        raise TypeError(f"'relative' should be a boolean")

    if band is None:
        band = [0.5, 30]
    if not isinstance(band, list):
        raise TypeError(
            f"'band' should be a list of tuple(s)," f"e.g. [0.5, 30], got {type(band)}"
        )

    # Define STFT parameters
    nperseg = int(win_sec * sf)
    noverlap = int(nperseg - (step * sf))

    f, t, Sxx = stft(
        signal, sf, nperseg=nperseg, nfft=nfft, noverlap=noverlap, padded=False, boundary="zeros"
    )

    f = np.array([round(each, 2) for each in f])

    idx_f = np.logical_and(f >= band[0], f <= band[1])
    f = f[idx_f]
    Sxx = Sxx[idx_f, :]
    Sxx = np.square(np.abs(Sxx))

    if norm:
        sum_power = Sxx.sum(0).reshape(1, -1)
        np.divide(Sxx, sum_power, out=Sxx)

    return f, t, Sxx


def band_power(psd, freq, bands=None, relative=False):
    """Compute the band power

    Parameters
    ----------
    psd : np.array
        Array of power spectrum density
    freq : np.array
        Array of frequncy for psd
    bands : list, optional
        Multiple or one frequency band. e.g.
        [[0.5, 4, 'delta], [4, 9, 'theta']]

    Returns
    -------
    band_dict : dict
        e.g.
        {
        'delta': value of delta band power,
        'theta': value of theta band power
        }

    Note
    ----
    Use the composite Simpson's rule.
    Inspired by https://raphaelvallat.com/bandpower.html
    """

    freq_res = freq[1] - freq[0]
    band_dict = {}
    for each in bands:
        idx_band = np.logical_and(freq >= each[0], freq <= each[1])
        bp = simps(psd[idx_band], dx=freq_res)

        if relative:
            bp /= simps(psd, dx=freq_res)

        band_dict[each[2]] = bp

    return band_dict
