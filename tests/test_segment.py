# -*- coding: UTF-8 -*-
"""Tests for state-based segmentation."""

import numpy as np

from misleep.data import MiAnnotation, MiData
from misleep.preprocessing.segment import crop_state_data


def test_crop_state_data():
    sf = 256.0
    md = MiData(
        signals=[np.ones(int(sf * 100)), np.zeros(int(sf * 100))],
        channels=["EEG", "EMG"],
        sf=[sf, sf],
        time="20240409-18:00:00",
    )
    # 50 s NREM, 50 s Wake
    anno = MiAnnotation(sleep_state=[1] * 50 + [3] * 50)

    nrem, rem, wake, init = crop_state_data(md, anno)
    assert nrem.duration == 50
    assert wake.duration == 50
    assert rem.duration == 0
    assert init.duration == 0
    # NREM data: EEG channel all ones; Wake data: EMG channel all zeros
    assert np.allclose(nrem.signals[0], 1.0)
    assert np.allclose(wake.signals[1], 0.0)
