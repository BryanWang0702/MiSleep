# -*- coding: UTF-8 -*-
"""
@Project: MiSleep_v2 
@File: annotation_io.py
@Author: Xueqiang Wang
@Date: 2024/3/6
@Description:  Annotation io, default is for MiSleep annotation, `NAME.txt`
"""
from misleep.io.base import MiAnnotation
from misleep.utils.annotation import marker2mianno, start_end2mianno, sleep_state2mianno


def load_misleep_anno(file_path):
    """
    Load annotations from misleep annotation file

    Parameters
    ----------
    file_path : str
        Path of annotation file
    """

    # Read out the annotation file and split by `\n` to get each line
    annotation = open(file_path, 'r').read().split('\n')
    if annotation == [""]:
        raise AssertionError("Empty")
    try:
        marker_idx = annotation.index('==========Marker==========')
        start_end_idx = annotation.index('==========Start-End==========')
        try:
            sleep_state_idx = annotation.index('==========Sleep state==========')
        except ValueError:
            sleep_state_idx = annotation.index('==========Sleep stage==========')
    except Exception:
        raise AssertionError("Invalid")

    marker = annotation[marker_idx + 1: start_end_idx]
    marker = marker2mianno(marker)

    start_end = annotation[start_end_idx + 1: sleep_state_idx]
    start_end = start_end2mianno(start_end)

    sleep_state = annotation[sleep_state_idx + 1:]
    sleep_state = sleep_state2mianno(sleep_state)

    return MiAnnotation(sleep_state=sleep_state, start_end=start_end, marker=marker)
