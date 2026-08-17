# -*- coding: UTF-8 -*-
"""Miscellaneous helpers shared across MiSleep."""

import os
from collections import Counter

from misleep.data.annotation import MiAnnotation


def create_new_mianno(data_duration):
    """Create a fresh :class:`MiAnnotation` with all states set to Init (4).

    Parameters
    ----------
    data_duration : int
        Duration of the recording in seconds.

    Returns
    -------
    MiAnnotation
    """
    marker = []
    start_end = []
    sleep_state = [4 for _ in range(data_duration)]
    return MiAnnotation(sleep_state=sleep_state, start_end=start_end, marker=marker)


def identify_startend_color(color_dict, state_name, end=False):
    """Return the color of a state name from a mapping, or ``'blue'`` as fallback."""
    if state_name in color_dict.keys():
        return color_dict[state_name]
    return "blue"


def get_base_path(file_path):
    """Strip a known data-file extension from a path.

    Returns the path without ``.txt``/``.xlsx``/``.mat``/``.edf``/``.csv``
    when present, otherwise the input unchanged.
    """
    base, ext = os.path.splitext(file_path)
    if ext in [".txt", ".xlsx", ".mat", ".edf", ".csv"]:
        return base
    return file_path


def downsample_by_most_frequent(lst, group_size=5):
    """Downsample a list by taking the most frequent element per chunk.

    Parameters
    ----------
    lst : list
        Input sequence.
    group_size : int
        Chunk size. Default is 5.

    Returns
    -------
    list
        One representative value per chunk.
    """
    result = []
    for i in range(0, len(lst), group_size):
        group = lst[i:i + group_size]
        if group:
            counter = Counter(group)
            most_common = counter.most_common(1)[0][0]
            result.append(most_common)
    return result
