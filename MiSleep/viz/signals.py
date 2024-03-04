# -*- coding: UTF-8 -*-
"""
@Project: MiSleep_v2 
@File: signals.py
@Author: Xueqiang Wang
@Date: 2024/3/1
@Description:  Visualization signals
"""

import matplotlib.pyplot as plt
from MiSleep.io.base import MiData


def plot_signals(midata, ch_names=None):
    """
    Plot midata with selected channels and start end period
    Parameters
    ----------
    midata : MiData
        Original data
    ch_names : list, optional
        List of channels to plot. Default is None, means all channels

    Returns
    -------

    """
    if not isinstance(midata, MiData):
        raise TypeError(f"'midata' must be an instance of MiData, got {type(midata)}")

    if ch_names is None or ch_names == []:
        ch_names = midata.channels

    if not isinstance(ch_names, list):
        raise TypeError(f"'chans' should be a list, got {type(ch_names)}")

    signals = []
    channels = []
    sf = []
    for chan in ch_names:
        if chan in midata.channels:
            chan_idx = midata.channels.index(chan)
            signals.append(midata.signals[chan_idx])
            channels.append(chan)
            sf.append(midata.sf[chan_idx])
        else:
            raise IndexError(f"{chan} channel is not in the signal channels ({midata.channels})")

    fig = plt.figure()
    axs = fig.subplots(nrows=len(channels), ncols=1)
    if len(channels) == 1:
        axs = [axs]
    fig.set_tight_layout(True)
    fig.tight_layout(h_pad=0, w_pad=0)
    fig.subplots_adjust(hspace=0)  # Adjust subplots

    for i in range(len(channels)):
        axs[i].plot(signals[i], color='black', linewidth=0.5)
        y_lim = max(signals[i][:int(60 * sf[i])])
        axs[i].set_ylim(ymin=-y_lim, ymax=y_lim)
        axs[i].set_xlim(xmin=0, xmax=len(signals[i]))
        axs[i].xaxis.set_ticks([])
        axs[i].yaxis.set_ticks([])
        axs[i].set_ylabel(f"{channels[i]}\n{y_lim:.2e}")
    axs[-1].set_xticks([int(each*sf[-1]) for each in
                        range(0, midata.duration, 5)],
                       range(0, midata.duration, 5),
                       rotation=45)
    axs[-1].set_xticks([int(each*sf[-1]) for each in
                        range(0, midata.duration)], minor=True)

    return fig, axs
