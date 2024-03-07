# -*- coding: UTF-8 -*-
"""
@Project: misleep
@File: test_signals_viz.py
@Author: Xueqiang Wang
@Date: 2024/3/1
@Description:  
"""
import unittest

from misleep.io.signal_io import load_mat
from misleep.viz.signals import plot_signals


class TestMiData(unittest.TestCase):
    def test_viz(self):
        midata = load_mat(r'../datasets/20240114_male2_nf.mat')
        cropped_midata = midata.crop([30, 100])
        fig, axs = plot_signals(signals=cropped_midata.signals, ch_names=cropped_midata.channels,
                                sf=cropped_midata.sf)
        fig.show()
