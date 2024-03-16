# -*- coding: UTF-8 -*-
"""
@Project: MiSleep_v2 
@File: annotation.py
@Author: Xueqiang Wang
@Date: 2024/3/6
@Description:  
"""
from itertools import groupby

from misleep.io.base import MiAnnotation


def lst2group(pre_lst):
    """
    Convert a list like [[1, 2], [2, 2], [3, 2], [4, 2], [5, 2], [6, 1], [7, 1], [8, 1], [9, 3], [10, 3]] to
    [[1, 5, 2], [6, 8, 1], [9, 10, 3]]
    :param pre_lst:
    :return:
    """

    # Convert to [[[1, 2], [2, 2], [3, 2], [4, 2], [5, 2]], [[6, 1], [7, 1], [8, 1]], [[9, 3], [10, 3]]]
    pre_lst = [list(group) for idx, group in groupby(pre_lst, key=lambda x: x[1])]

    # Convert to [[1, 5, 2], [6, 8, 1], [9, 10, 3]]
    return [[each[0][0], each[-1][0], each[0][1]] for each in pre_lst]


def marker2mianno(marker):
    """
    Transfer MiSleep annotation to [[1, 'injection'], 20, 'injection'], ...] format
    """
    if marker != [] or marker is not None:
        marker = [each.split(', ') for each in marker]
        marker = [[int(each[1]), each[7]] for each in marker]
        return marker
    return []


def start_end2mianno(start_end):
    """Transfer start_end to [[1, 20, 'spindle'], [30, 50, 'SWA'], ...]"""
    if start_end != [] or start_end is not None:
        start_end = [each.split(', ') for each in start_end]
        start_end = [[int(each[1]), int(each[4]), each[7]] for each in start_end]
        return start_end
    return []


def sleep_state2mianno(sleep_state):
    """Transfer sleep_state to [1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, ...]"""
    start_end = [each.split(', ') for each in sleep_state]
    return [item for each in start_end for item in [int(each[6])] * (int(each[4]) - int(each[1]) + 1)]


def create_new_mianno(data_duration):
    """Create a new MiAnnotation object"""
    marker = []
    start_end = []
    sleep_state = [4 for _ in range(data_duration)]
    return MiAnnotation(sleep_state=sleep_state, start_end=start_end, marker=marker)
