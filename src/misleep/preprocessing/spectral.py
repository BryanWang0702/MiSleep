# -*- coding: UTF-8 -*-
"""Spectral analysis: Welch power spectrum, spectrogram and band power."""

import numpy as np
from scipy.integrate import simpson
from scipy.ndimage import gaussian_filter1d
from scipy.signal import stft, welch

from misleep.preprocessing.filtering import signal_filter


def _select_frequency_band(freq, power, band):
    """Crop on the true FFT axis and interpolate exact band endpoints.

    Fractional sample rates and integer FFT lengths need not place a bin
    exactly on the requested limits. Never round bins before selecting them
    or relabel an out-of-band bin as the boundary. Interpolate power between
    the two surrounding bins instead, without extrapolating beyond the axis.
    The frequency dimension is the first axis of ``power``.
    """
    low, high = band
    selected = (freq >= low) & (freq <= high)
    result_freq = freq[selected]
    result_power = power[selected]
    for boundary, prepend in ((low, True), (high, False)):
        if not freq[0] <= boundary <= freq[-1]:
            continue
        if np.any(result_freq == boundary):
            continue
        right = np.searchsorted(freq, boundary)
        left = right - 1
        weight = (boundary - freq[left]) / (freq[right] - freq[left])
        value = power[left] + weight * (power[right] - power[left])
        if prepend:
            result_freq = np.concatenate(([boundary], result_freq))
            result_power = np.concatenate((value[np.newaxis], result_power))
        else:
            result_freq = np.concatenate((result_freq, [boundary]))
            result_power = np.concatenate((result_power, value[np.newaxis]))
    return result_freq, result_power


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
    psd = gaussian_filter1d(psd, sigma=gaussian_sigma) if gaussian_sigma is not None else psd

    freq, psd = _select_frequency_band(freq, psd, band)

    total_power = simpson(psd, x=freq)
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

    Sxx = np.square(np.abs(Sxx))
    f, Sxx = _select_frequency_band(f, Sxx, band)

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
    band_dict = {}
    for each in bands:
        band_freq, band_psd = _select_frequency_band(freq, psd, each[:2])
        bp = simpson(band_psd, x=band_freq)

        if relative:
            total = simpson(psd, x=freq)
            if total > 0:
                bp /= total

        band_dict[each[2]] = bp

    return band_dict
