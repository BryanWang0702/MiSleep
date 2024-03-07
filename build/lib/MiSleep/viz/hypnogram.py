# -*- coding: UTF-8 -*-
"""
@Project: MiSleep_v2 
@File: hypnogram.py
@Author: Xueqiang Wang
@Date: 2024/3/5
@Description:  
"""

import matplotlib.pyplot as plt


def plot_hypno(sleep_state, state_map=None):
    """
    Draw hypnogram with sleep_state list

    Parameters
    ----------
    sleep_state : list
        List of sleep state, should be integers, and use state_map map to contents
    state_map : dict
        Dict of mapping from sleep state content to it's meaning
    """

    if not isinstance(sleep_state, list):
        raise TypeError(f"'sleep_state' should be a list, got {type(sleep_state)}")

    if state_map is None:
        state_map = {
            1: 'NREM',
            2: 'REM',
            3: 'Wake',
            4: 'Init'
        }
    fig = plt.figure(figsize=(20, 3))
    ax = fig.subplots(nrows=1, ncols=1)
    ax.step(range(len(sleep_state)), sleep_state, where='mid', linewidth=1)
    ax.set_ylim(0.5, max(state_map.keys()) + 0.5)
    ax.set_xlim(0, len(sleep_state) - 1)
    ax.yaxis.set_ticks(list(state_map.keys()), list(state_map.values()))

    return fig, ax
