# -*- coding: UTF-8 -*-
"""
@Project: MiSleep_v2 
@File: test_midata.py
@Author: Xueqiang Wang
@Date: 2024/2/29
@Description:  Test class for MiData
"""
import unittest

from MiSleep.io.base import MiData
from MiSleep.io.signal_io import load_edf, load_mat


class TestMiData(unittest.TestCase):
    def test_load(self):
        midata = load_mat(r'./datasets/test_format_mat.mat')
        print(midata.sf)
        print(midata.channels)
        print(len(midata.signals))
        print(midata._duration)

        midata = load_edf(r'./datasets/learn-nsrr01.edf')
        print(midata.sf)
        print(midata.channels)
        print(len(midata.signals))
        print(midata._duration)

    def test_rename_channel(self):
        midata = load_edf(r'./datasets/learn-nsrr01.edf')
        print(midata.channels)
        midata.rename_channels({'PR': 'UNKNOW'})
        print(midata.channels)
        # Not exit will raise IndexError
        midata.rename_channels({'PR': 'UNKNOW', 'NOTEXIT': 'fault'})
        print(midata.channels)

    def test_differential(self):
        midata = load_edf(r'../../datasets/learn-nsrr01.edf')
        # Not exist will raise IndexError
        midata.differential(chan1='SaO2', chan2='not_exist')
        # if sample frequency not match, can't do differential, raise ValueError
        midata.differential(chan1='SaO2', chan2='EEG')

    def test_filter(self):
        midata = load_edf(r'../../datasets/learn-nsrr01.edf')
        # chans must be a list, even only one channel to filter
        midata.filter(chans=['EEG', 'EMG'], btype='bandstop', high=5)
