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
from MiSleep.utils.signals import signal_filter


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

    def differential(self, chan1=None, chan2=None):
        """Do differential with specified channels (chan1 - chan2)"""
        if chan1 is None or chan2 is None:
            raise ValueError(f"Specify two channel names to do differential")

        if chan1 not in self._channels:
            raise IndexError(f"{chan1} is not in the channel names ({self._channels})")

        if chan2 not in self._channels:
            raise IndexError(f"{chan2} is not in the channel names ({self._channels})")

        chan1_idx = self._channels.index(chan1)
        chan2_idx = self._channels.index(chan2)
        if self._signals[chan1_idx].shape[0] != self._signals[chan2_idx].shape[0]:
            raise ValueError(f"Channel {chan1} and channel {chan2} got different dimension to do differential "
                             f"({self._signals[chan1_idx].shape} and {self._signals[chan2_idx].shape})")
        self._signals.append(self._signals[chan1_idx] - self._signals[chan2_idx])
        self._channels.append(f"{chan1}_{chan2}_diff")
        self._sf.append(self._sf[chan1_idx])
        self._n_channels = len(self._channels)

    def rename_channels(self, mapping):
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

    def filter(self, chans=None, btype='lowpass', low=0.5, high=30):
        """
        Filter the specified channel(s) and get new channels
        Parameters
        ----------
        chans : list
            Channels to be filtered, should be a list of channels
        btype : {'bandpass', 'lowpass', 'highpass', 'bandstop'}, optional
            The type of filter.  Default is 'lowpass'.
        low : float
        high : float
        """
        if chans is None or not isinstance(chans, list):
            raise ValueError(f"'chans' should be a list of channel names, got {type(chans)}")

        for chan in chans:
            if chan in self._channels:
                chan_idx = self._channels.index('chans')
                filtered_data, fname = signal_filter(
                    data=self._signals[chan_idx],
                    btype=btype, sf=self._sf[chan_idx], low=low, high=high)
                self._signals.append(filtered_data)
                self._channels.append(f"{chan}_{fname}")
                self._sf.append(self._sf[chan_idx])
                self._n_channels = len(self._channels)
            else:
                raise IndexError(f"{chan} channel is not in the signal channels ({self._channels})")

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

    @property
    def sf(self, idx=None):
        """Sample frequency of all signal channels, with idx (start from zero) for specified channel"""
        if idx is None:
            return self._sf
        if idx >= self._n_channels:
            raise IndexError(
                f"Index {idx} can't larger than the signal channels number {self._n_channels}")

        return self._sf[idx]
