# -*- coding: UTF-8 -*-
"""
@Project: misleep
@File: test_spectral_viz.py
@Author: Xueqiang Wang
@Date: 2024/3/4
@Description:  
"""
import unittest

from misleep.io.signal_io import load_mat, load_edf
from misleep.preprocessing.spectral import spectrum, spectrogram
from misleep.viz.spectral import plot_spectrum, plot_spectrogram
from scipy import signal


class TestMiData(unittest.TestCase):
    def test_viz_spectrum(self):
        midata = load_mat(r'./datasets/test_format_mat.mat')
        EEG_F_midata = midata.pick_chs(ch_names=['EEG_F'])
        freq, psd = spectrum(signal=EEG_F_midata.signals[0],
                             sf=EEG_F_midata.sf[0], win_sec=5)
        fig, ax = plot_spectrum(freq, psd)
        fig.show()

    def test_viz_spectrogram(self):
        midata = load_mat(r'./datasets/test_format_mat.mat')
        EEG_F_midata = midata.pick_chs(ch_names=['EEG_F'])

        # EEG_F_midata.filter(chans=['ch1'], btype='bandpass', low=0.5, high=30)
        cropped = EEG_F_midata.crop(time_period=[0, 200])
        f, t, Sxx = spectrogram(signal=cropped.signals[0],
                                sf=cropped.sf[0], step=0.2, window=2, norm=True)
        fig, ax = plot_spectrogram(f, t, Sxx, percentile=99.7)
        ax.set_ylim(0.5, 30)
        fig.show()
