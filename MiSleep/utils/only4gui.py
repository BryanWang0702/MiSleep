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


def plot_signal_area4GUI(midata, start, duration, spec, spec_percentile, y_lim, y_shift):
    """Plot signal area for GUI
    Parameters
    ----------
    midata : MiData
        All preprocessings were done, only plot in this function
    start : start position
    duration : plot duration
    spec : List
        Spectrogram values, create by misleep.preprocessing.spectral.spectrogram, e.g. [f, t, Sxx]
    spec_percentile : float
        Percentile for spectrogram vmax
    y_lim : y lim for signals
    y_shift : y shift for signals
    """
    fig = plt.figure()
    axs = fig.subplots(nrows=midata.n_channel + 1, ncols=1)
    fig.set_tight_layout(True)
    fig.tight_layout(h_pad=0, w_pad=0)
    fig.subplots_adjust(hspace=0)  # Adjust subplots

    f, t, Sxx = spec
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


def plot_spec4GUI():
    pass