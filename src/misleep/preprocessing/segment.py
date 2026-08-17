# -*- coding: UTF-8 -*-
"""Segmentation of signals by sleep state.

The :func:`crop_state_data` helper splits a recording into per-state
sub-recordings (NREM / REM / Wake / Init) based on the annotation.
"""

from copy import deepcopy

import numpy as np

from misleep.data import MiData
from misleep.utils.annotation import lst2group


def crop_state_data(midata, mianno):
    """Split the data into per-state sub-recordings.

    The sleep-state sequence is grouped into consecutive runs; the samples
    of every run of the same state are concatenated, and a new
    :class:`MiData` is returned per state.

    Parameters
    ----------
    midata : MiData
        The recording to split.
    mianno : MiAnnotation
        The annotation defining the states.

    Returns
    -------
    (NREM_data, REM_data, Wake_data, Init_data) : tuple of MiData
        One data container per state, with ``describe`` set accordingly.
        States not present in the annotation yield empty signals.
    """
    sleep_state = deepcopy(mianno.sleep_state)
    sleep_state = lst2group([[idx, each] for idx, each in enumerate(sleep_state)])
    signals = deepcopy(midata.signals)

    state_signals = {1: [], 2: [], 3: [], 4: []}
    for idx, signal in enumerate(signals):
        sf = midata.sf[idx]
        for state in state_signals:
            state_data = [signal[int(each[0] * sf): int(each[1] * sf)]
                          for each in sleep_state if each[2] == state]
            state_signals[state].append(
                np.array([element for sublist in state_data for element in sublist]))

    names = {1: "NREM", 2: "REM", 3: "Wake", 4: "Init"}
    results = []
    for state in (1, 2, 3, 4):
        results.append(MiData(
            signals=state_signals[state],
            channels=midata.channels,
            sf=midata.sf,
            time=midata.time,
            describe=f"{names[state]} cropped data"))

    return tuple(results)
