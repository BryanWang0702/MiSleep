# -*- coding: UTF-8 -*-
"""
@Project: MiSleep_v2 
@File: hypnogram.py
@Author: Xueqiang Wang
@Date: 2024/3/5
@Description:  
"""

import matplotlib.pyplot as plt
import matplotlib


def plot_hypno(sleep_state, state_map=None, time_range=[0, -1]):
    """
    Draw hypnogram with sleep_state list

    Parameters
    ----------
    sleep_state : list
        List of sleep state, should be integers, and use state_map map to contents
    state_map : dict
        Dict of mapping from sleep state content to it's meaning
    time_range : list
        Time range to plot the hypnogram
    """

    if not isinstance(sleep_state, list):
        raise TypeError(f"'sleep_state' should be a list, got {type(sleep_state)}")
    
    try:
        if time_range != [0, -1]:
            sleep_state_ = sleep_state[time_range[0]:time_range[1]]
    except Exception as e:
        print("Invalid time range, plot as default")
        sleep_state_ = sleep_state

    sleep_state = sleep_state_

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
