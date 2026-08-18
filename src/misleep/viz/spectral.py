# -*- coding: UTF-8 -*-
"""Visualization of spectral results (spectrum and spectrogram)."""

import matplotlib.pyplot as plt
import numpy as np


def spectrogram_color_limits(Sxx, percentile=99.7):
    """Return a stable v2-style power color range for a spectrogram.

    Spectrogram power is non-negative. Anchoring the lower limit at zero and
    clipping only the brightest tail at ``percentile`` keeps the low-power
    background dark and the EEG bands easy to distinguish.
    """
    if not isinstance(percentile, (int, float)) or not 0 < percentile <= 100:
        raise ValueError("'percentile' must be greater than 0 and at most 100")
    values = np.asarray(Sxx)
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return 0.0, 1.0
    vmax = float(np.percentile(finite, percentile))
    if vmax <= 0:
        vmax = float(np.max(finite)) if np.max(finite) > 0 else 1.0
    return 0.0, vmax


def plot_spectrum(f, p):
    """Plot a power spectrum.

    Parameters
    ----------
    f : array_like
        Frequency bins.
    p : array_like
        Power values.

    Returns
    -------
    (fig, ax) : tuple
        The matplotlib figure and axis.
    """
    fig = plt.figure(figsize=(10, 8))
    ax = fig.subplots(nrows=1, ncols=1)
    ax.plot(f, p)
    y_lim = max(p) * 1.1
    ax.set_ylim(0, y_lim)
    ax.set_xlim(0, f[-1])
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Power spectral density (Power/Hz)")

    return fig, ax


def plot_spectrogram(f, t, Sxx, percentile=100, band=None, color_bar=False):
    """Plot a spectrogram.

    Parameters
    ----------
    f : ndarray
        Frequency bins.
    t : ndarray
        Time bins.
    Sxx : ndarray
        Spectrogram values.
    percentile : float, optional
        Color-scale upper percentile. Default is 100.
    band : list, optional
        Y-axis frequency limits, e.g. ``[0.5, 30]``.
    color_bar : bool
        Whether to draw a color bar.

    Returns
    -------
    (fig, ax) : tuple
        The matplotlib figure and axis.
    """
    if not isinstance(percentile, (int, float)):
        raise TypeError(f"'percentile' should be a float between 0~100, got {percentile}")

    cmap = plt.get_cmap("jet")
    vmin, vmax = spectrogram_color_limits(Sxx, percentile)
    fig = plt.figure(figsize=(15, 4))
    ax = fig.subplots(nrows=1, ncols=1)
    if band is not None:
        ax.set_ylim(band[0], band[1])

    if color_bar:
        pcm = ax.pcolormesh(t, f, Sxx, cmap=cmap, vmin=vmin, vmax=vmax,
                            shading="auto")
        fig.colorbar(pcm, ax=ax)
    else:
        ax.pcolormesh(t, f, Sxx, cmap=cmap, vmin=vmin, vmax=vmax,
                      shading="auto")
    ax.set_facecolor(cmap(0.0))
    ax.set_xlabel("Time (S)")
    ax.set_ylabel("Frequency (HZ)")

    return fig, ax
