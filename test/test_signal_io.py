# -*- coding: UTF-8 -*-
"""
@Project: misleep
@File: test_signal_io.py
@Author: Xueqiang Wang
@Date: 2024/2/22
@Description:
"""

import pytest
from misleep.io.signal_io import load_mat, load_edf, write_mat, write_edf
from time import time
import os


class TestSignalIO():
    def test_load_mat(self):
        """Test load_mat"""
        mat_path = r'./test/test_data/10mins_example_mat.mat'
        s = time()
        midata = load_mat(data_path=mat_path)
        e = time()
        print(f"Load data from .mat file, cost {e-s} seconds\n"
              f"Signals shape {len(midata.signals)}, \nchannels: {midata.channels}, \nsampling frequency: {midata.sf}, \nacquisition time: {midata.time}")

    def test_load_edf(self):
        """Test load_edf"""
        edf_path = r'./test/test_data/10mins_example_edf.edf'
        s = time()
        midata = load_edf(data_path=edf_path)
        e = time()
        print(f"Load data from .edf file, cost {e-s} seconds\n"
              f"Signals shape {len(midata.signals)}, \nchannels: {midata.channels}, \nsampling frequency: {midata.sf}, \nacquisition time: {midata.time}")

    def test_write_mat(self):
        """Test write_mat"""
        mat_path = r'./test/test_data/10mins_example_mat.mat'
        s = time()
        midata = load_mat(data_path=mat_path)
        e = time()
        print(f"Load data from .mat file, cost {e-s} seconds\n"
              f"Signals shape {len(midata.signals)}, \nchannels: {midata.channels}, \nsampling frequency: {midata.sf}, \nacquisition time: {midata.time}")

        write_mat(midata.signals, midata.channels, midata.sf, midata.time, 
                  r'./test/test_data/10mins_example_mat_saved_by_python.mat')
        print('Saved to .mat successfully')

    def test_write_edf(self):
        """Test write_edf"""
        mat_path = r'./test/test_data/10mins_example_mat.mat'
        s = time()
        midata = load_mat(data_path=mat_path)
        e = time()
        print(f"Load data from .mat file, cost {e-s} seconds\n"
              f"Signals shape {len(midata.signals)}, \nchannels: {midata.channels}, \nsampling frequency: {midata.sf}, \nacquisition time: {midata.time}")

        write_edf(midata.signals, midata.channels, midata.sf, midata.time, 
                  r'./test/test_data/10mins_example_mat_saved_by_python.edf')
        print('Saved to .edf successfully')

    def test_load_written_edf(self):
        """Test load written edf"""
        edf_path = r'./test/test_data/10mins_example_mat_saved_by_python.edf'
        s = time()
        midata = load_edf(data_path=edf_path)
        e = time()
        print(f"Load data from .mat file, cost {e-s} seconds\n"
              f"Signals shape {len(midata.signals)}, \nchannels: {midata.channels}, \nsampling frequency: {midata.sf}, \nacquisition time: {midata.time}")
        
    def test_load_written_mat(self):
        """Test load written mat"""
        mat_path = r'./test/test_data/10mins_example_mat_saved_by_python.mat'
        s = time()
        midata = load_mat(data_path=mat_path)
        e = time()
        print(f"Load data from .mat file, cost {e-s} seconds\n"
              f"Signals shape {len(midata.signals)}, \nchannels: {midata.channels}, \nsampling frequency: {midata.sf}, \nacquisition time: {midata.time}")
