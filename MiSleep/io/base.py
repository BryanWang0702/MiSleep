# -*- coding: UTF-8 -*-
"""
@Project: MiSleep_v2 
@File: base.py
@Author: Xueqiang Wang
@Date: 2024/2/28
@Description:  
"""
import math

import numpy as np


class MiData:
    """
    MiSleep data format, basically contains signals, channel name, channel sample frequency
    """

    def __init__(self, signals, channels, sf):
        if isinstance(signals, list) or isinstance(signals, np.ndarray):
            for each in signals:
                if not isinstance(each, np.ndarray):
                    raise ValueError(f"Signals should be a list of arrays or ndarray, got {type(each)}")
        else:
            raise ValueError(f"Signals should be a list of arrays or ndarray, got {type(signals)}")

        if isinstance(channels, list):
            if len(channels) != len(signals):
                raise ValueError(
                    f"Length of channels {len(channels)} don't match the length of signals ({len(signals)})")
            for each in channels:
                if not isinstance(each, str):
                    raise ValueError(f"Channels should be a list of strings, got {type(each)}")
        else:
            raise ValueError(f"Channels should be a list of strings, got {type(channels)}")

        if isinstance(sf, list):
            if len(sf) != len(signals):
                raise ValueError(
                    f"Length of sample frequency {len(sf)} don't match the length of signals ({len(signals)})")
            for each in sf:
                if not isinstance(each, float):
                    raise ValueError(f"Sample frequency should be a list of float, got {type(each)}")
        else:
            raise ValueError(f"Sample frequency should be a list of float, got {type(sf)}")

        # Verify the duration of each signal channel, and modify to a same integer duration in second
        temp_duration = set([math.floor(len(signals[idx]) / each) for idx, each in sf])
        if len(temp_duration) != 1:
            raise ValueError(f"The duration of all signal channels have 1 seconds in difference.")

        self._duration = list(temp_duration)[0]
        self._signals = [signals[idx][:self._duration * each] for idx, each in sf]
        self._channels = channels
        self._n_channels = len(self._channels)
        self._sf = sf

    @property
    def sf(self, idx=None):
        """Sample frequency of all signal channels, with idx (start from zero) for specified channel"""
        if idx is None:
            return self._sf
        if idx >= self._n_channels:
            raise IndexError(
                f"Index {idx} can't larger than the signal channels number {self._n_channels}")

        return self._sf[idx]

    @property
    def duration(self):
        """Duration of the signal recording"""
        return self._duration

    @property
    def signals(self):
        """Signals data field"""
        return self._signals

    @property
    def channels(self):
        """Channel name for each signal channel"""
        return self._channels

    @channels.setter
    def channels(self, mapping):
        """
        Set new channels name with mapping
        Parameters
        ----------
        mapping : dict
            Map the old channel name to a new channel name
        """
        if isinstance(mapping, dict):
            for idx, each in enumerate(self._channels):
                if each in mapping.keys():
                    self._channels[idx] = mapping[each]
        else:
            raise ValueError(
                f"Mapping should be a dict which map old channel name to a new one, got {type(mapping)}")
