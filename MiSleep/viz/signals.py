# -*- coding: UTF-8 -*-
"""
@Project: MiSleep_v2 
@File: signals.py
@Author: Xueqiang Wang
@Date: 2024/3/1
@Description:  Visualization signals
"""

import matplotlib.pyplot as plt


def plot_signals(midata, chans=None, start_end=None):
    """
    Plot midata with selected channels and start end period
    Parameters
    ----------
    midata : MiData
        Original data
    chans : list, optional
        List of channels to plot. Default is None, means all channels
    start_end : list, optional
        Start second and end second. Default is [0, 60]

    Returns
    -------

    """
    if chans is None:
        chans = midata.channels

    if not isinstance(chans, list):
        raise TypeError(f"'chans' should be a list, got {type(chans)}")

    if start_end is None:
        start_end = [0, 60]

    if not isinstance(start_end, list):
        raise TypeError(f"'start_end' should be a list of two integers, got {type(start_end)}")

    if len(start_end) != 2:
        raise ValueError(f"'start_end' should be a list of two integers, got {start_end}")

    if not isinstance(start_end[0], int) or not isinstance(start_end[1], int):
        raise TypeError(f"'start_end' should be a list of two integers, "
                        f"got {type(start_end[0])} and {type(start_end[1])} ")

    signals = []
    channels = []
    sf = []
    for chan in chans:
        if chan in midata.channels:
            chan_idx = midata.channels.index(chan)
            signals.append(midata.signals[chan_idx][
                           int(start_end[0] * midata.sf[chan_idx]): int(start_end[1] * midata.sf[chan_idx])])
            channels.append(chan)
            sf.append(midata.sf[chan_idx])
        else:
            raise IndexError(f"{chan} channel is not in the signal channels ({midata.channels})")

    fig = plt.figure()
    axs = fig.subplots(nrows=len(channels), ncols=1)
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
                        range(0, start_end[1]-start_end[0], 5)],
                       range(start_end[0], start_end[1], 5),
                       rotation=45)
    axs[-1].set_xticks([int(each*sf[-1]) for each in
                        range(0, start_end[1]-start_end[0])], minor=True)

    return fig, axs
