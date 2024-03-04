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
                    raise TypeError(f"Signals should be a list of arrays or ndarray, got {type(each)}")
        else:
            raise TypeError(f"Signals should be a list of arrays or ndarray, got {type(signals)}")

        if isinstance(channels, list):
            if len(channels) != len(signals):
                raise ValueError(
                    f"Length of channels {len(channels)} don't match the length of signals ({len(signals)})")
            for each in channels:
                if not isinstance(each, str):
                    raise TypeError(f"Channels should be a list of strings, got {type(each)}")
        else:
            raise TypeError(f"Channels should be a list of strings, got {type(channels)}")

        if isinstance(sf, list):
            if len(sf) != len(signals):
                raise ValueError(
                    f"Length of sample frequency {len(sf)} don't match the length of signals ({len(signals)})")
            for each in sf:
                if not isinstance(each, float):
                    raise TypeError(f"Sample frequency should be a list of float, got {type(each)}")
        else:
            raise TypeError(f"Sample frequency should be a list of float, got {type(sf)}")

        # Verify the duration of each signal channel, and modify to a same integer duration in second
        temp_duration = set([math.floor(len(signals[idx]) / each) for idx, each in enumerate(sf)])
        if len(temp_duration) != 1:
            raise ValueError(f"The duration of all signal channels are different.")

        self._duration = list(temp_duration)[0]
        self._signals = [signals[idx][:int(self._duration * each)] for idx, each in enumerate(sf)]
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
        self.add(self._signals[chan1_idx] - self._signals[chan2_idx],
                 f"{chan1}_{chan2}_diff", self._sf[chan1_idx])

    def rename_channels(self, mapping):
        """
        Set new channels name with mapping
        Parameters
        ----------
        mapping : dict
            Map the old channel name to a new channel name
        """
        if isinstance(mapping, dict):
            for each in mapping.keys():
                if each not in self._channels:
                    raise IndexError(f"{each} is not in the signal channel list ({self._channels})")
                else:
                    self._channels[self._channels.index(each)] = mapping[each]
        else:
            raise TypeError(
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
            raise TypeError(f"'chans' should be a list of channel names, got {type(chans)}")

        for chan in chans:
            if chan in self._channels:
                chan_idx = self._channels.index(chan)
                filtered_data, fname = signal_filter(
                    data=self._signals[chan_idx],
                    btype=btype, sf=self._sf[chan_idx], low=low, high=high)
                self.add(filtered_data, f"{chan}_{fname}", self._sf[chan_idx])
            else:
                raise IndexError(f"{chan} channel is not in the signal channels ({self._channels})")

    def add(self, signal, channel, sf):
        """
        Add signal, and other information
        Parameters
        ----------
        signal : array
        channel : str
        sf : float
        Returns
        -------

        """
        _duration = math.floor(len(signal) / sf)
        if np.abs(_duration - self._duration) > 10:
            raise ValueError(f"The new added signal channel's duration ({_duration}) "
                             f"is different with original signals ({self._duration})")

        if not isinstance(channel, str):
            raise TypeError(f"Channel name should be a string, got {type(channel)}")
        if not isinstance(sf, (int, float)):
            raise TypeError(f"Sample frequency should be a float, got {type(sf)}")

        self._signals.append(signal)
        self._channels.append(channel)
        self._n_channels = len(self._channels)
        self._sf.append(sf)

    def delete(self, channel=None):
        """Delete channel by channel name"""
        if not isinstance(channel, str):
            raise TypeError(f"Channel name should be a string, got {type(channel)}")
        if channel not in self._channels:
            raise IndexError(f"Channel name {channel} is not in the signal channels ({self._channels})")
        if len(self._channels) == 1:
            raise ValueError(f"Channel {channel} is the last channel of signal data, you can't delete it")
        chan_idx = self._channels.index(channel)
        self._signals.pop(chan_idx)
        self._channels.pop(chan_idx)
        self._sf.pop(chan_idx)
        self._n_channels = len(self._channels)

    def crop(self, time_period):
        """Crop a period of signals with the time_period (in seconds)"""
        if not isinstance(time_period, list):
            raise TypeError(f"'time_period' should be a list of two positive integers, got {type(time_period)}")

        if len(time_period) != 2:
            raise ValueError(f"'time_period' should be a list of two positive integers, got {time_period}")

        if time_period[0] < 0 or time_period[1] < 0 or \
                not isinstance(time_period[0], int) or not isinstance(time_period[1], int):
            raise TypeError(f"'time_period' should be a list of two positive integers, "
                            f"got {type(time_period[0])} and {type(time_period[1])} ")

        if time_period[0] >= time_period[1]:
            raise ValueError(f"End time (got {time_period[1]}) of 'time_period' should "
                             f"be larger than start time (got {time_period[0]})")

        if time_period[1] > self._duration:
            time_period[1] = self._duration

        signals = [self.signals[idx][int(time_period[0]*each): int(time_period[1]*each)]
                   for idx, each in enumerate(self.sf)]
        channels = self.channels
        sf = self.sf

        return MiData(signals=signals, channels=channels, sf=sf)

    def pick_chs(self, ch_names):
        """Pick specified channels"""
        if ch_names is None or ch_names == []:
            ch_names = self.channels

        if not isinstance(ch_names, list):
            raise TypeError(f"'ch_names' should be a list, got {type(ch_names)}")

        signals = []
        sf = []
        channels = []
        for chan in ch_names:
            if chan in self.channels:
                chan_idx = self.channels.index(chan)
                signals.append(self.signals[chan_idx])
                sf.append(self.sf[chan_idx])
                channels.append(chan)
            else:
                raise IndexError(f"{chan} channel is not in the signal channels ({self.channels})")

        return MiData(signals=signals, channels=channels, sf=sf)

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
