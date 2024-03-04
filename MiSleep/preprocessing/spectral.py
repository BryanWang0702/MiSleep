# -*- coding: UTF-8 -*-
"""
@Project: MiSleep_v2 
@File: spectral.py
@Author: Xueqiang Wang
@Date: 2024/3/4
@Description:  Spectrum, time-frequency (spectrogram) analysis
"""

from MiSleep.io.base import MiData


def spectrum(midata, ch_names=None, power_band=None):
    """

    Parameters
    ----------
    midata : MiData
    ch_names : list, optional
        Default is None -> all channels
    power_band : list, optional
        List of frequency  bands of interests. Each tuple should contain the lower and upper frequencies,
        as well as the band name (e.g. (0.5, 4, 'Delta'))
    Returns
    -------
    freq : list
    power : list
    """
    if not isinstance(midata, MiData):
        raise TypeError(f"'midata' should be an instance of MiData, got {type(midata)}")
    if ch_names is None or ch_names == []:
        ch_names = midata.channels
