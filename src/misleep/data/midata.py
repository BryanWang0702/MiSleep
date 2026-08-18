# -*- coding: UTF-8 -*-
"""Core signal data container :class:`MiData`.

``MiData`` is the primary in-memory representation of a polysomnographic
recording inside MiSleep. It stores, for every channel:

* the signal samples (1-D numpy arrays),
* the channel name,
* the sampling frequency of the channel.

It also stores the recording start time and an optional free-text
description, and exposes a small set of in-place or copy-on-write
operations (filter, differential, crop, pick, rename, add, delete).

All channels of a :class:`MiData` object share the same integer duration
in seconds (the minimum integer duration across channels); longer
channels are truncated accordingly.
"""

import math

import numpy as np


def _unique_name(name, existing):
    """Return ``name`` or the next available ``name_N`` variant."""
    if name not in existing:
        return name
    index = 1
    while f"{name}_{index}" in existing:
        index += 1
    return f"{name}_{index}"


class MiData:
    """MiSleep signal data format.

    Parameters
    ----------
    signals : list or ndarray
        List of 1-D arrays, one per channel.
    channels : list of str
        Channel name for each signal channel, e.g. ``['EEG_F', 'EEG_P', 'EMG']``.
    sf : list of float
        Sampling frequency of each signal channel, e.g. ``[256., 256., 256.]``.
    time : str
        Recording start time in string format, e.g. ``'20240228-19:45:00'``.
    describe : str, optional
        Free-text description of the data. Defaults to ``''``.
    """

    def __init__(self, signals, channels, sf, time, describe=None):
        self._validate_inputs(signals, channels, sf, describe)

        self._describe = "" if describe is None else describe
        self._time = time

        # Avoid duplicated channel names: append "_1", "_2", ...
        temp_channel = []
        for each in channels:
            temp_channel.append(_unique_name(each, temp_channel))
        channels = temp_channel

        # All channels are truncated to the same integer duration in seconds
        temp_duration = [math.floor(len(signals[idx]) / each) for idx, each in enumerate(sf)]
        self._duration = min(temp_duration)

        self._signals = [signals[idx][: int(self._duration * each)] for idx, each in enumerate(sf)]
        self._channels = channels
        self._n_channels = len(self._channels)
        self._sf = sf

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _validate_inputs(signals, channels, sf, describe):
        if not isinstance(signals, (list, np.ndarray)):
            raise TypeError(f"Signals should be a list of arrays or ndarray, got {type(signals)}")
        if len(signals) == 0:
            raise ValueError("At least one signal channel is required")
        for each in signals:
            if not isinstance(each, np.ndarray):
                raise TypeError(f"Signals should be a list of arrays or ndarray, got {type(each)}")
            if each.ndim != 1:
                raise ValueError(f"Each signal must be a 1-D array, got shape {each.shape}")

        if not isinstance(channels, list):
            raise TypeError(f"Channels should be a list of strings, got {type(channels)}")
        if len(channels) != len(signals):
            raise ValueError(
                f"Length of channels ({len(channels)}) does not match the length of signals ({len(signals)})"
            )
        for each in channels:
            if not isinstance(each, str):
                raise TypeError(f"Channels should be a list of strings, got {type(each)}")

        if not isinstance(sf, list):
            raise TypeError(f"Sample frequency should be a list of int or float, got {type(sf)}")
        if len(sf) != len(signals):
            raise ValueError(
                f"Length of sample frequency ({len(sf)}) does not match the length of signals ({len(signals)})"
            )
        for each in sf:
            if not isinstance(each, (int, float)):
                raise TypeError(f"Sample frequency should be a list of int or float, got {type(each)}")
            if not math.isfinite(each) or each <= 0:
                raise ValueError(f"Sample frequencies must be finite and positive, got {each}")

        if describe is not None and not isinstance(describe, str):
            raise TypeError(f"'describe' should be a string for data description, got {type(describe)}")

    # ------------------------------------------------------------------
    # In-place operations
    # ------------------------------------------------------------------
    def differential(self, chan1=None, chan2=None):
        """Compute the differential signal ``chan1 - chan2`` and add it as a new channel.

        Parameters
        ----------
        chan1 : str
            Name of the first channel.
        chan2 : str
            Name of the second channel.
        """
        if chan1 is None or chan2 is None:
            raise ValueError("Specify two channel names to do differential")

        if chan1 not in self._channels:
            raise IndexError(f"{chan1} is not in the channel names ({self._channels})")
        if chan2 not in self._channels:
            raise IndexError(f"{chan2} is not in the channel names ({self._channels})")

        chan1_idx = self._channels.index(chan1)
        chan2_idx = self._channels.index(chan2)
        if self._signals[chan1_idx].shape[0] != self._signals[chan2_idx].shape[0]:
            raise ValueError(
                f"Channel {chan1} and channel {chan2} have different lengths to do differential "
                f"({self._signals[chan1_idx].shape} and {self._signals[chan2_idx].shape})"
            )
        self.add(self._signals[chan1_idx] - self._signals[chan2_idx],
                 f"{chan1}_{chan2}_DIFF", self._sf[chan1_idx])

    def rename_channels(self, mapping):
        """Rename channels in place with a mapping.

        Parameters
        ----------
        mapping : dict
            Map old channel name to a new channel name.
        """
        if not isinstance(mapping, dict):
            raise TypeError(f"Mapping should be a dict which maps old channel name to a new one, got {type(mapping)}")

        for each in mapping.keys():
            if each not in self._channels:
                raise IndexError(f"{each} is not in the signal channel list ({self._channels})")
            new_name = mapping[each]
            if not isinstance(new_name, str) or not new_name.strip():
                raise ValueError("New channel names must be non-empty strings")
            index = self._channels.index(each)
            existing = self._channels[:index] + self._channels[index + 1:]
            self._channels[index] = _unique_name(new_name.strip(), existing)

    def filter(self, chans=None, btype="bandpass", low=0.5, high=30):
        """Filter the specified channel(s) and add the result as new channel(s).

        Parameters
        ----------
        chans : list of str
            Channels to be filtered.
        btype : {'bandpass', 'lowpass', 'highpass', 'bandstop'}, optional
            The type of filter. Default is ``'bandpass'``.
        low : float
            Lower cutoff frequency in Hz.
        high : float
            Higher cutoff frequency in Hz.
        """
        from misleep.preprocessing.filtering import signal_filter

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
        """Add a new signal channel to the data.

        Parameters
        ----------
        signal : ndarray
            The signal samples.
        channel : str
            Channel name.
        sf : float
            Sampling frequency of the new channel.
        """
        if not isinstance(signal, np.ndarray) or signal.ndim != 1 or signal.size == 0:
            raise ValueError("The new signal must be a non-empty 1-D numpy array")
        if not isinstance(channel, str):
            raise TypeError(f"Channel name should be a string, got {type(channel)}")
        if not isinstance(sf, (int, float)) or not math.isfinite(sf) or sf <= 0:
            raise TypeError(f"Sample frequency should be a float, got {type(sf)}")

        _duration = math.floor(len(signal) / sf)
        if _duration < self._duration:
            raise ValueError(
                f"The new signal is shorter ({_duration}s) than the existing data "
                f"({self._duration}s)")

        channel = _unique_name(channel, self.channels)

        self._signals.append(signal[:int(self._duration * sf)])
        self._channels.append(channel)
        self._n_channels = len(self._channels)
        self._sf.append(sf)

    def delete(self, channel=None):
        """Delete a channel by name.

        Parameters
        ----------
        channel : str
            Name of the channel to delete.
        """
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

    # ------------------------------------------------------------------
    # Copy-on-write operations
    # ------------------------------------------------------------------
    def crop(self, time_period):
        """Return a new :class:`MiData` cropped to ``[start, end]`` seconds.

        Parameters
        ----------
        time_period : list of two ints
            Start and end second of the crop.

        Returns
        -------
        MiData
            Cropped data (all channels).
        """
        if not isinstance(time_period, list) or len(time_period) != 2:
            raise TypeError(f"'time_period' should be a list of two positive integers, got {time_period}")

        if time_period[0] < 0 or time_period[1] < 0 or \
                not isinstance(time_period[0], int) or not isinstance(time_period[1], int):
            raise TypeError(
                f"'time_period' should be a list of two positive integers, "
                f"got {type(time_period[0])} and {type(time_period[1])}")

        if time_period[0] >= time_period[1]:
            raise ValueError(
                f"End time (got {time_period[1]}) of 'time_period' should be larger than start time (got {time_period[0]})")

        start, end = time_period
        end = min(end, self._duration)

        signals = [self.signals[idx][int(start * each): int(end * each)]
                   for idx, each in enumerate(self.sf)]
        return MiData(signals=signals, channels=self.channels, sf=self.sf,
                      time=self.time, describe=self.describe)

    def pick_chs(self, ch_names):
        """Return a new :class:`MiData` with only the requested channels.

        Parameters
        ----------
        ch_names : list of str
            Channels to keep.

        Returns
        -------
        MiData
            Data restricted to the selected channels.
        """
        if ch_names is None or ch_names == []:
            ch_names = self.channels

        if not isinstance(ch_names, list):
            raise TypeError(f"'ch_names' should be a list, got {type(ch_names)}")

        signals, sf, channels = [], [], []
        for chan in ch_names:
            if chan in self.channels:
                chan_idx = self.channels.index(chan)
                signals.append(self.signals[chan_idx])
                sf.append(self.sf[chan_idx])
                channels.append(chan)
            else:
                raise IndexError(f"{chan} channel is not in the signal channels ({self.channels})")

        return MiData(signals=signals, channels=channels, sf=sf,
                      time=self.time, describe=self.describe)

    def reorder_channels(self, new_order):
        """Reorder the channels in place.

        Parameters
        ----------
        new_order : list of str
            Channel names in the desired order (must be a permutation of
            the current channel names).
        """
        if sorted(new_order) != sorted(self._channels):
            raise ValueError(
                f"'new_order' must be a permutation of the channel names "
                f"({self._channels}), got {new_order}")

        order_idx = [self._channels.index(name) for name in new_order]
        self._signals = [self._signals[i] for i in order_idx]
        self._channels = [self._channels[i] for i in order_idx]
        self._sf = [self._sf[i] for i in order_idx]
        self._n_channels = len(self._channels)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def duration(self):
        """Duration of the recording in integer seconds."""
        return self._duration

    @property
    def signals(self):
        """List of signal arrays (one per channel)."""
        return self._signals

    @property
    def channels(self, idx=None):
        """Channel names (all, or the one at index ``idx``)."""
        if idx is None:
            return self._channels
        if idx >= self._n_channels:
            raise IndexError(f"Index {idx} can't be larger than the signal channels number {self._n_channels}")
        return self._channels[idx]

    @property
    def sf(self, idx=None):
        """Sampling frequencies (all, or the one at index ``idx``)."""
        if idx is None:
            return self._sf
        if idx >= self._n_channels:
            raise IndexError(f"Index {idx} can't be larger than the signal channels number {self._n_channels}")
        return self._sf[idx]

    @property
    def time(self):
        """Recording start time as a string."""
        return self._time

    @property
    def describe(self):
        """Free-text description of the data."""
        return self._describe

    @property
    def n_channels(self):
        """Number of channels."""
        return self._n_channels

    def get_channel_index(self, channel):
        """Return the index of a channel by name."""
        return self._channels.index(channel)

    def __repr__(self):
        summary = ", ".join(f"{ch}@{sf:.0f}Hz" for ch, sf in zip(self._channels, self._sf))
        return f"MiData(duration={self._duration}s, channels=[{summary}], time='{self._time}')"
