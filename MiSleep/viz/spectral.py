# -*- coding: UTF-8 -*-
"""
@Project: misleep
@File: spectral.py
@Author: Xueqiang Wang
@Date: 2024/3/4
@Description:  
"""

import matplotlib.pyplot as plt
import numpy as np


def plot_spectrum(f, p):
    """

    Parameters
    ----------
    f : List
        Frequency of spectrum
    p : List
        Power of each frequency bin
    Returns
    -------
    fig :
    ax :
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


def plot_spectrogram(f, t, Sxx, percentile=100, band=None):
    """Plot the spectrogram, percentile is for color adjustment"""
    if not isinstance(percentile, (int, float)):
        raise TypeError(f"'percentile' should be a float between 0~100, got {percentile}")

    cmap = plt.cm.get_cmap('jet')
    fig = plt.figure(figsize=(15, 4))
    ax = fig.subplots(nrows=1, ncols=1)
    if band is not None:
        ax.set_ylim(band[0], band[1])
    pcm = ax.pcolormesh(t, f, Sxx, cmap=cmap, vmax=np.percentile(Sxx, percentile))
    fig.colorbar(pcm, ax=ax)
    ax.set_xlabel("Time (S)")
    ax.set_ylabel("Frequency (HZ)")

    return fig, ax
