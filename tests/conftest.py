# -*- coding: UTF-8 -*-
"""Shared pytest fixtures: synthetic signals and a fresh config."""

import numpy as np
import pytest

from helpers import make_emg, make_signal  # noqa: F401  (re-exported for tests)


@pytest.fixture
def midata():
    from misleep.data import MiData

    sf = 256.0
    return MiData(
        signals=[make_signal(sf=sf), make_emg(sf=sf)],
        channels=["EEG", "EMG"],
        sf=[sf, sf],
        time="20240409-18:00:00",
        describe="synthetic test data",
    )


@pytest.fixture
def mianno():
    from misleep.data import MiAnnotation

    sleep_state = [4] * 100 + [1] * 300 + [2] * 100 + [3] * 100
    return MiAnnotation(
        sleep_state=sleep_state,
        marker=[[30.5, "injection"]],
        start_end=[[50, 70, "spindle"]],
    )


@pytest.fixture
def fresh_config(tmp_path, monkeypatch):
    """A config loaded with the user dir redirected to a temp folder."""
    monkeypatch.setenv("MISLEEP_DATA_DIR", str(tmp_path))
    from misleep import config as config_module
    from misleep.logger import get_data_dir

    orig = config_module.get_data_dir

    def fake_data_dir():
        return tmp_path

    monkeypatch.setattr(config_module, "get_data_dir", fake_data_dir)
    # reload the logger data dir too
    monkeypatch.setattr("misleep.logger.get_data_dir", fake_data_dir)
    return config_module.load_config()
