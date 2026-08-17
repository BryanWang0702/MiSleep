# -*- coding: UTF-8 -*-
"""Helpers shared by the test modules."""

import numpy as np


def make_signal(sf=256.0, duration=600, seed=0):
    """Return a synthetic EEG-like signal with clear rhythmic content."""
    rng = np.random.default_rng(seed)
    t = np.arange(int(sf * duration)) / sf
    signal = (2.0 * np.sin(2 * np.pi * 1.0 * t)      # delta
              + 1.0 * np.sin(2 * np.pi * 6.0 * t)    # theta
              + 0.5 * np.sin(2 * np.pi * 12.0 * t)   # spindle band
              + 0.3 * np.sin(2 * np.pi * 25.0 * t))  # beta
    signal += 0.2 * rng.standard_normal(signal.shape)
    return signal.astype(np.float64)


def make_emg(sf=256.0, duration=600, seed=1):
    """Return a synthetic EMG-like signal (high-frequency noise bursts)."""
    rng = np.random.default_rng(seed)
    t = np.arange(int(sf * duration)) / sf
    signal = 0.5 * np.sin(2 * np.pi * 60 * t) + 0.2 * rng.standard_normal(t.size)
    return signal.astype(np.float64)
