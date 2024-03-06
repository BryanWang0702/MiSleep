# -*- coding: UTF-8 -*-
"""
@Project: MiSleep_v2 
@File: test_annotation_io.py
@Author: Xueqiang Wang
@Date: 2024/3/6
@Description:  
"""
import unittest

from misleep import plot_hypno
from misleep import load_misleep_anno


class TestSignalIO(unittest.TestCase):
    def test_load_anno(self):
        mianno = load_misleep_anno(file_path='../datasets/20240114_male2_nf.txt')
        fig, ax = plot_hypno(mianno.sleep_state[0:36000])
        fig.show()
