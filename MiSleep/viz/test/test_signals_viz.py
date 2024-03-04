# -*- coding: UTF-8 -*-
"""
@Project: MiSleep_v2 
@File: test_signals_viz.py
@Author: Xueqiang Wang
@Date: 2024/3/1
@Description:  
"""
import unittest

from MiSleep.io.signal_io import load_edf, load_mat
from MiSleep.viz.signals import plot_signals


class TestMiData(unittest.TestCase):
    def test_viz(self):
        midata = load_mat(r'./datasets/test_format_mat.mat')
        cropped_midata = midata.crop([30, 56])
        fig, axs = plot_signals(midata=cropped_midata)
        fig.show()

        # midata = load_edf(r'./datasets/learn-nsrr01.edf')
        # fig, axs = plot_signals(midata=midata, start_end=[30, 60])
        # fig.show()
