# -*- coding: UTF-8 -*-
"""
@Project: MiSleep_v2 
@File: test_signal_io.py
@Author: Xueqiang Wang
@Date: 2024/2/22
@Description:

Issue 20240222
The sampling frequency for each channel could be different, so the sampling frequency information
should be stored in the data file as a list, just like the channel name... Inspired from EDF file,
there is a list for samples.
"""

import unittest
import pytest
from MiSleep.io.signal_io import load_mat, load_edf, load_npz, \
    write_npz, write_edf, write_mat
from time import time


class TestSignalIO(unittest.TestCase):
    def test_load_mat_write_edf(self):
        """Test load_mat and write_edf"""
        mat_path = r'../../datasets/test_mat.mat'
        s = time()
        signals, channels = load_mat(data_path=mat_path)
        e = time()
        print(f"Load data from .mat file, cost {e-s} seconds\n"
              f"Signals shape {signals.shape}, channels: {channels}")

        write_edf(signals, channels, 305, '../../datasets/test_edf.edf')
        print('Saved to .edf successfully')

    def test_load_edf_write_npz(self):
        """Test load_edf and write_npz"""
        edf_path = r'../../datasets/learn-nsrr01.edf'
        s = time()
        signals, channels = load_edf(data_path=edf_path)
        e = time()
        print(f"Load data from .edf file, cost {e-s} seconds\n"
              f"Signals shape {signals.shape}, channels: {channels}")

        write_npz(signals, channels, '../../datasets/test_npz.npz')
        print('Saved to .npz successfully')

    def test_load_npz_write_mat(self):
        """Test load_npz and write_mat"""
        npz_path = r'../../datasets/test_npz.npz'
        s = time()
        signals, channels = load_npz(data_path=npz_path)
        e = time()
        print(f"Load data from .npz file, cost {e-s} seconds\n"
              f"Signals shape {signals.shape}, channels: {channels}")

        write_mat(signals, channels, r'../../datasets/test_mat.mat')
        print('Saved to .mat successfully')


