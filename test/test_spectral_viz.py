# -*- coding: UTF-8 -*-
"""
@Project: misleep
@File: test_spectral_viz.py
@Author: Xueqiang Wang
@Date: 2024/3/4
@Description:  
"""
import unittest

from misleep.io.signal_io import load_mat
from misleep.preprocessing.spectral import spectrum, spectrogram
from misleep.viz.spectral import plot_spectrum, plot_spectrogram


class TestMiData(unittest.TestCase):
    def test_viz_spectrum(self):
        midata = load_mat(r'../datasets/rem_data.mat')
        EEG_F_midata = midata.pick_chs(ch_names=['ch3'])
        freq, psd = spectrum(signal=EEG_F_midata.signals[0],
                             sf=EEG_F_midata.sf[0], win_sec=5)
        fig, ax = plot_spectrum(freq, psd)
        fig.show()

    def test_viz_spectrogram(self):
        midata = load_mat(r'../datasets/rem_data.mat')
        EEG_F_midata = midata.pick_chs(ch_names=['ch3'])

        # EEG_F_midata.filter(chans=['ch1'], btype='bandpass', low=0.5, high=30)
        cropped = EEG_F_midata.crop([0, 38200])
        f, t, Sxx = spectrogram(signal=cropped.signals[0],
                                sf=cropped.sf[0], step=1, window=5, norm=True)
        fig, ax = plot_spectrogram(f, t, Sxx, percentile=99)
        ax.set_ylim(0.5, 30)
        fig.show()
