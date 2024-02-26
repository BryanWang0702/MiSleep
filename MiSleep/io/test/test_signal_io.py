# -*- coding: UTF-8 -*-
"""
@Project: MiSleep_v2 
@File: test_signal_io.py
@Author: Xueqiang Wang
@Date: 2024/2/22
@Description:
"""

import unittest
from MiSleep.io.signal_io import load_mat, load_edf, write_mat
from time import time


class TestSignalIO(unittest.TestCase):
    def test_load_mat_write_mat(self):
        """Test load_mat and write_mat"""
        mat_path = r'../../datasets/mat_from_mat.mat'
        s = time()
        signals, channels, sf = load_mat(data_path=mat_path)
        e = time()
        print(f"Load data from .mat file, cost {e-s} seconds\n"
              f"Signals shape {len(signals)}, channels: {channels}, sampling frequency: {sf}")

        write_mat(signals, channels, sf, r'../../datasets/mat_from_mat_.mat')
        print('Saved to .mat successfully')

    def test_load_edf_write_mat(self):
        """Test load_edf and write_mat"""
        edf_path = r'../../datasets/learn-nsrr01.edf'
        s = time()
        signals, channels, sf = load_edf(data_path=edf_path)
        e = time()
        print(f"Load data from .edf file, cost {e-s} seconds\n"
              f"Signals shape {len(signals)}, channels: {channels}, sampling frequency: {sf}")

        write_mat(signals, channels, sf, r'../../datasets/mat_from_edf.mat')
        print('Saved to .mat successfully')
