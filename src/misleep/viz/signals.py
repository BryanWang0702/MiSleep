# -*- coding: UTF-8 -*-
"""Visualization of raw signals."""

import math

import matplotlib.pyplot as plt


def plot_signals(signals, sf=None, ch_names=None):
    """Plot one or several signal channels on a shared time axis.

    Parameters
    ----------
    signals : list of ndarray
        Signal data, one array per channel.
    sf : list of float, optional
        Sampling frequency of each channel.
    ch_names : list of str, optional
        Channel names. Defaults to ``None`` (all channels, generic labels).

    Returns
    -------
    (fig, axs) : tuple
        The matplotlib figure and axes.
    """
    duration = math.floor(len(signals[0]) / sf[0])
    fig = plt.figure(figsize=(duration * 0.3 if duration < 60 else 18, 1 * len(signals)))
    axs = fig.subplots(nrows=len(signals), ncols=1)
    if len(signals) == 1:
        axs = [axs]
    fig.tight_layout(h_pad=0, w_pad=0)
    fig.subplots_adjust(hspace=0)

    for i in range(len(signals)):
        axs[i].plot(signals[i], color="black", linewidth=0.5)
        y_lim = max(signals[i][:int(60 * sf[i])])
        axs[i].set_ylim(ymin=-y_lim, ymax=y_lim)
        axs[i].set_xlim(xmin=0, xmax=len(signals[i]))
        axs[i].xaxis.set_ticks([])
        axs[i].yaxis.set_ticks([])
        name = ch_names[i] if ch_names is not None else f"ch{i + 1}"
        axs[i].set_ylabel(f"{name}\n{y_lim:.2e}")

    axs[-1].set_xticks(
        [int(each * sf[-1]) for each in range(0, duration, 5)],
        range(0, duration, 5),
        rotation=45,
    )
    axs[-1].set_xticks([int(each * sf[-1]) for each in range(0, duration)], minor=True)

    return fig, axs
