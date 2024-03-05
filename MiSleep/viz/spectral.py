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


def plot_spectrum(f, p, background=False):
    """

    Parameters
    ----------
    f : List
        Frequency of spectrum
    p : List
        Power of each frequency bin
    background : bool
         Whether plot the background of each band
         0.5~4  Delta
         4~7    Theta
         7~12   Alpha
         12~30  Beta
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

    if background:
        idx_delta = f[np.logical_and(f >= 0.5, f <= 4)]
        idx_theta = f[np.logical_and(f >= 4, f <= 7)]
        idx_alpha = f[np.logical_and(f >= 7, f <= 12)]
        idx_beta = f[np.logical_and(f >= 12, f <= 30)]
        ax.fill_between(idx_delta, [0] * len(idx_delta), [y_lim] * len(idx_delta),
                        color='#ffe0c0')
        ax.fill_between(idx_theta, [0] * len(idx_theta), [y_lim] * len(idx_theta),
                        color='#ffffe0')
        ax.fill_between(idx_alpha, [0] * len(idx_alpha), [y_lim] * len(idx_alpha),
                        color='#ccf9e8')
        ax.fill_between(idx_beta, [0] * len(idx_beta), [y_lim] * len(idx_beta),
                        color='#c8def9')

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
