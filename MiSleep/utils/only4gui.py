# -*- coding: UTF-8 -*-
"""
@Project: MiSleep_v2 
@File: only4gui.py
@Author: Xueqiang Wang
@Date: 2024/3/8
@Description:  
"""
import numpy as np
from matplotlib import pyplot as plt

from misleep.preprocessing.spectral import spectrogram


def plot_signal_area4GUI(midata, start, duration, spec_idx, spec_percentile, y_lim):
    """Plot signal area for GUI
    Parameters
    ----------
    midata : MiData
    start : start position
    duration : plot duration
    spec_idx : choose which channel to plot spectrogram
    spec_percentile : colorbar percentage for spectrogram
    y_lim : y lim for signals
    """
    fig = plt.figure()
    axs = fig.subplots(nrows=midata.n_channel + 1, ncols=1)
    fig.set_tight_layout(True)
    fig.tight_layout(h_pad=0, w_pad=0)
    fig.subplots_adjust(hspace=0)  # Adjust subplots

    f, t, Sxx = spectrogram(signal=midata.signals[spec_idx],
                            sf=midata.sf[spec_idx],
                            step=1, window=5, norm=True)
    cmap = plt.cm.get_cmap('jet')
    axs[0].set_ylim(0, 30)
    axs[0].pcolormesh(t, f, Sxx, cmap=cmap,
                      vmax=np.percentile(Sxx, spec_percentile))

    for i in range(midata.n_channel):
        axs[i + 1].plot(midata.signals[i], color='black', linewidth=0.5)
        y_lim = max(midata.signals[i][:int(60 * midata.sf[i])])
        axs[i + 1].set_ylim(ymin=-y_lim, ymax=y_lim)
        axs[i + 1].set_xlim(xmin=0, xmax=len(midata.signals[i]))
        axs[i + 1].xaxis.set_ticks([])
        axs[i + 1].yaxis.set_ticks([])
        axs[i + 1].set_ylabel(f"{midata.channels[i]}\n{y_lim:.2e}")
    axs[-1].set_xticks([int(each * midata.sf[-1]) for each in
                        range(0, duration, 5)],
                       range(0, duration, 5),
                       rotation=45)
    axs[-1].set_xticks([int(each * midata.sf[-1]) for each in
                        range(0, duration)], minor=True)

    return fig, axs
