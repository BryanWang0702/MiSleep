# -*- coding: UTF-8 -*-
"""Spectral analysis: Welch power spectrum, spectrogram and band power."""

import numpy as np
from scipy.integrate import simpson
from scipy.ndimage import gaussian_filter1d
from scipy.signal import stft, welch

from misleep.preprocessing.filtering import signal_filter


def spectrum(signal, sf, band=None, relative=True, win_sec=1, nfft=None, gaussian_sigma=None):
    """Calculate the (Welch) power spectrum of a signal.

    The signal is band-pass filtered to ``band`` first, then the power
    spectral density is estimated with :func:`scipy.signal.welch`.

    Parameters
    ----------
    signal : ndarray
        1-D signal.
    sf : float
        Sampling frequency.
    band : list, optional
        Frequency band of interest, e.g. ``[0.5, 30]``. Default is ``[0.5, 30]``.
    relative : bool
        Whether to normalize the PSD so it integrates to 1.
    win_sec : int
        Window length (in seconds) for the FFT.
    nfft : int, optional
        Number of FFT points.
    gaussian_sigma : float, optional
        Sigma for Gaussian smoothing of the PSD.

    Returns
    -------
    freq : ndarray
        Frequency bins.
    psd : ndarray
        Power spectral density.
    """
    if not isinstance(signal, np.ndarray):
        raise TypeError(f"'signal' should be a numpy array, got {type(signal)}")
    if not isinstance(sf, (int, float)):
        raise TypeError(f"'sf' should be an integer or float, got {type(sf)}")
    if not isinstance(relative, bool):
        raise TypeError("'relative' should be a boolean")

    if band is None:
        band = [0.5, 30]
    if not isinstance(band, list):
        raise TypeError(f"'band' should be a list, e.g. [0.5, 4], got {type(band)}")

    signal, _ = signal_filter(data=signal, sf=sf, btype="bandpass", low=band[0], high=band[1])

    freq, psd = welch(signal, sf, nperseg=int(sf * win_sec), nfft=nfft, scaling="density")
    freq = np.array([round(each, 2) for each in freq])
    psd = gaussian_filter1d(psd, sigma=gaussian_sigma) if gaussian_sigma is not None else psd

    idx_freq = np.logical_and(freq >= band[0], freq <= band[1])
    freq = freq[idx_freq]
    psd = psd[idx_freq]

    total_power = simpson(psd, dx=freq[1] - freq[0])
    if relative and total_power > 0:
        psd /= total_power

    return freq, psd


def spectrogram(signal, sf, band=None, step=0.2, win_sec=2, norm=False, nfft=None):
    """Calculate the spectrogram of a signal with the STFT.

    Parameters
    ----------
    signal : ndarray
        1-D signal.
    sf : float
        Sampling frequency.
    band : list, optional
        Frequency band of interest, e.g. ``[0.5, 30]``.
    step : float
        Step (in seconds) between STFT windows.
    win_sec : float
        Window length (in seconds) for the STFT.
    norm : bool
        Whether to normalize the power across frequencies at each time point.
    nfft : int, optional
        Number of FFT points.

    Returns
    -------
    f : ndarray
        Frequency bins.
    t : ndarray
        Time bins.
    Sxx : ndarray
        Spectrogram (squared magnitude of the STFT).
    """
    if not isinstance(signal, np.ndarray):
        raise TypeError(f"'signal' should be a numpy array, got {type(signal)}")
    if not isinstance(sf, (int, float)):
        raise TypeError(f"'sf' should be an integer or float, got {type(sf)}")

    if step > win_sec:
        raise ValueError(f"'step' ({step}) should be smaller than 'win_sec' ({win_sec})")
    step = 1 / sf if step <= 0 else step

    if not isinstance(norm, bool):
        raise TypeError("'norm' should be a boolean")

    if band is None:
        band = [0.5, 30]
    if not isinstance(band, list):
        raise TypeError(f"'band' should be a list, e.g. [0.5, 30], got {type(band)}")

    nperseg = int(win_sec * sf)
    noverlap = int(nperseg - (step * sf))

    f, t, Sxx = stft(signal, sf, nperseg=nperseg, nfft=nfft,
                     noverlap=noverlap, padded=False, boundary="zeros")

    f = np.array([round(each, 2) for each in f])

    idx_f = np.logical_and(f >= band[0], f <= band[1])
    f = f[idx_f]
    Sxx = Sxx[idx_f, :]
    Sxx = np.square(np.abs(Sxx))

    if norm:
        sum_power = Sxx.sum(0).reshape(1, -1)
        np.divide(Sxx, sum_power, out=Sxx, where=sum_power != 0)

    return f, t, Sxx


def band_power(psd, freq, bands=None, relative=False):
    """Compute the band power of a PSD.

    Parameters
    ----------
    psd : ndarray
        Power spectral density values.
    freq : ndarray
        Frequencies corresponding to ``psd``.
    bands : list, optional
        Frequency bands, e.g. ``[[0.5, 4, 'delta'], [4, 9, 'theta']]``.
    relative : bool
        Whether to express each band power relative to the total power.

    Returns
    -------
    dict
        Band name -> band power.
    """
    freq_res = freq[1] - freq[0]
    band_dict = {}
    for each in bands:
        idx_band = np.logical_and(freq >= each[0], freq <= each[1])
        bp = simpson(psd[idx_band], dx=freq_res)

        if relative:
            total = simpson(psd, dx=freq_res)
            if total > 0:
                bp /= total

        band_dict[each[2]] = bp

    return band_dict
