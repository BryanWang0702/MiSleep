# -*- coding: UTF-8 -*-
"""
@Project: misleep
@File: signals.py
@Author: Xueqiang Wang
@Date: 2024/3/1
@Description:  Visualization signals
"""
import math

import matplotlib.pyplot as plt


def plot_signals(signals, sf=None, ch_names=None):
    """
    Plot midata with selected channels and start end period
    Parameters
    ----------
    signals : List
        list of array
    sf : List of float
        sample frequency
    ch_names : List, optional
        List of channels to plot. Default is None, means all channels

    Returns
    -------

    """

    duration = math.floor(len(signals[0]) / sf[0])
    fig = plt.figure()
    axs = fig.subplots(nrows=len(signals), ncols=1)
    if len(signals) == 1:
        axs = [axs]
    fig.set_tight_layout(True)
    fig.tight_layout(h_pad=0, w_pad=0)
    fig.subplots_adjust(hspace=0)  # Adjust subplots

    for i in range(len(signals)):
        axs[i].plot(signals[i], color='black', linewidth=0.5)
        y_lim = max(signals[i][:int(60 * sf[i])])
        axs[i].set_ylim(ymin=-y_lim, ymax=y_lim)
        axs[i].set_xlim(xmin=0, xmax=len(signals[i]))
        axs[i].xaxis.set_ticks([])
        axs[i].yaxis.set_ticks([])
        axs[i].set_ylabel(f"{ch_names[i]}\n{y_lim:.2e}")
    axs[-1].set_xticks([int(each*sf[-1]) for each in
                        range(0, duration, 5)],
                       range(0, duration, 5),
                       rotation=45)
    axs[-1].set_xticks([int(each*sf[-1]) for each in
                        range(0, duration)], minor=True)

    return fig, axs
