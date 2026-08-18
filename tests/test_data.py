# -*- coding: UTF-8 -*-
"""Tests for the MiData / MiAnnotation data containers."""

import numpy as np
import pytest

from misleep.data import MiAnnotation, MiData


def test_midata_creation(midata):
    assert midata.n_channels == 2
    assert midata.duration == 600
    assert midata.channels == ["EEG", "EMG"]
    assert midata.sf == [256.0, 256.0]
    assert len(midata.signals) == 2
    assert midata.signals[0].shape == (600 * 256,)


def test_midata_validation():
    with pytest.raises(TypeError):
        MiData(signals=123, channels=["a"], sf=[1], time="t")
    with pytest.raises(TypeError):
        MiData(signals=[np.zeros(10)], channels=["a"], sf=["x"], time="t")
    with pytest.raises(ValueError):
        MiData(signals=[np.zeros(10), np.zeros(10)], channels=["a"], sf=[1], time="t")


def test_midata_duplicate_channels():
    md = MiData(signals=[np.zeros(10), np.zeros(10), np.zeros(10)],
                channels=["EEG", "EEG", "EEG"], sf=[1, 1, 1], time="t")
    assert md.channels == ["EEG", "EEG_1", "EEG_2"]


def test_midata_add_delete(midata):
    n = midata.n_channels
    midata.add(np.zeros(600 * 256), "EMG2", 256.0)
    assert midata.n_channels == n + 1
    assert "EMG2" in midata.channels
    # Duplicate name gets suffixed
    midata.add(np.zeros(600 * 256), "EMG2", 256.0)
    assert "EMG2_1" in midata.channels

    midata.delete("EMG2")
    assert "EMG2" not in midata.channels
    with pytest.raises(IndexError):
        midata.delete("NOT_A_CHANNEL")


def test_midata_crop(midata):
    cropped = midata.crop([100, 200])
    assert cropped.duration == 100
    assert cropped.signals[0].shape == (100 * 256,)
    assert cropped.channels == midata.channels
    # Cropping past the end clamps
    requested = [500, 9999]
    cropped2 = midata.crop(requested)
    assert cropped2.duration == 100
    assert requested == [500, 9999]  # caller input is not mutated


def test_midata_pick_chs(midata):
    picked = midata.pick_chs(["EMG"])
    assert picked.n_channels == 1
    assert picked.channels == ["EMG"]
    with pytest.raises(IndexError):
        midata.pick_chs(["NOT_A_CHANNEL"])


def test_midata_rename(midata):
    midata.rename_channels({"EEG": "EEG_F"})
    assert midata.channels[0] == "EEG_F"
    with pytest.raises(IndexError):
        midata.rename_channels({"NOT_A_CHANNEL": "x"})


def test_midata_rejects_invalid_signal_metadata():
    with pytest.raises(ValueError):
        MiData([], [], [], "t")
    with pytest.raises(ValueError):
        MiData([np.zeros((2, 2))], ["EEG"], [1], "t")
    with pytest.raises(ValueError):
        MiData([np.zeros(10)], ["EEG"], [0], "t")


def test_midata_filter(midata):
    midata.filter(chans=["EEG"], btype="bandpass", low=0.5, high=30)
    assert midata.n_channels == 3
    assert midata.channels[-1].startswith("EEG_bandpass")


def test_midata_differential(midata):
    midata.differential(chan1="EEG", chan2="EMG")
    assert midata.channels[-1] == "EEG_EMG_DIFF"
    with pytest.raises(ValueError):
        midata.differential(chan1="EEG")


def test_midata_repr(midata):
    assert "MiData" in repr(midata)


def test_midata_reorder_channels(midata):
    midata.reorder_channels(["EMG", "EEG"])
    assert midata.channels == ["EMG", "EEG"]
    assert midata.signals[0].shape == midata.signals[1].shape  # still consistent
    # not a permutation -> error
    with pytest.raises(ValueError):
        midata.reorder_channels(["EMG", "NOT_A_CHANNEL"])
    # reorder back
    midata.reorder_channels(["EEG", "EMG"])
    assert midata.channels == ["EEG", "EMG"]


def test_mianno_creation(mianno):
    assert mianno.anno_length == 600
    assert mianno.state_map == {1: "NREM", 2: "REM", 3: "Wake", 4: "Init"}
    assert mianno.marker == [[30.5, "injection"]]
    assert mianno.start_end == [[50, 70, "spindle"]]


def test_mianno_validation():
    with pytest.raises(TypeError):
        MiAnnotation(sleep_state="abc")
    with pytest.raises(ValueError):
        MiAnnotation(sleep_state=[1, 99])  # 99 not in default state map


def test_mianno_time_period(mianno):
    # sleep_state is a list; time filtering is done via slicing / list comprehension
    states = mianno.sleep_state[0:100]
    assert len(states) == 100
    markers = [m for m in mianno.marker if 0 <= m[0] <= 40]
    assert markers == [[30.5, "injection"]]
    assert [m for m in mianno.marker if 0 <= m[0] <= 10] == []
    events = [e for e in mianno.start_end if 40 <= e[0] and e[1] <= 80]
    assert events == [[50, 70, "spindle"]]


def test_mianno_custom_state_map():
    anno = MiAnnotation(sleep_state=[1, 2], state_map={1: "Slow", 2: "Fast"})
    assert anno.state_names == ["Slow", "Fast"]
