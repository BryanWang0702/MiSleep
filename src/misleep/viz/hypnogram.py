# -*- coding: UTF-8 -*-
"""Visualization of hypnograms."""

import matplotlib.pyplot as plt

DEFAULT_STATE_MAP = {1: "NREM", 2: "REM", 3: "Wake", 4: "Init"}


def plot_hypno(sleep_state, state_map=None, time_range=[0, -1]):
    """Draw a hypnogram from a per-second sleep state sequence.

    Parameters
    ----------
    sleep_state : list
        Per-second state codes (integers), interpreted through ``state_map``.
    state_map : dict, optional
        State code -> name mapping. Defaults to
        ``{1: 'NREM', 2: 'REM', 3: 'Wake', 4: 'Init'}``.
    time_range : list of two ints, optional
        Time window to plot, ``[start, end]`` seconds. Default plots all.

    Returns
    -------
    (fig, ax) : tuple
        The matplotlib figure and axis.
    """
    if not isinstance(sleep_state, list):
        raise TypeError(f"'sleep_state' should be a list, got {type(sleep_state)}")

    sleep_state_ = sleep_state
    if time_range != [0, -1]:
        try:
            sleep_state_ = sleep_state[time_range[0]:time_range[1]]
        except Exception:
            print("Invalid time range, plot as default")
            sleep_state_ = sleep_state

    if state_map is None:
        state_map = DEFAULT_STATE_MAP

    fig = plt.figure(figsize=(20, 3))
    ax = fig.subplots(nrows=1, ncols=1)
    ax.step(range(len(sleep_state_)), sleep_state_, where="mid", linewidth=1)
    ax.set_ylim(0.5, max(state_map.keys()) + 0.5)
    ax.set_xlim(0, len(sleep_state_) - 1)
    ax.yaxis.set_ticks(list(state_map.keys()), list(state_map.values()))

    return fig, ax
