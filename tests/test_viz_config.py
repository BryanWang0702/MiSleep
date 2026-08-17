# -*- coding: UTF-8 -*-
"""Tests for the visualization and config modules."""

import matplotlib

matplotlib.use("Agg")  # headless backend

import numpy as np  # noqa: E402
import pytest  # noqa: E402

from misleep.config import default_config_path, load_config, save_config  # noqa: E402
from misleep.viz import plot_hypno, plot_signals, plot_spectrogram, plot_spectrum  # noqa: E402


def test_plot_signals(midata):
    fig, axs = plot_signals(midata.signals, sf=midata.sf, ch_names=midata.channels)
    assert fig is not None
    assert len(axs) == 2
    import matplotlib.pyplot as plt

    plt.close(fig)


def test_plot_spectrum():
    freq = np.linspace(0.5, 30, 100)
    psd = np.random.default_rng(0).random(100) + 0.1
    fig, ax = plot_spectrum(freq, psd)
    import matplotlib.pyplot as plt

    plt.close(fig)


def test_plot_spectrogram():
    f = np.linspace(0.5, 30, 40)
    t = np.linspace(0, 10, 50)
    Sxx = np.random.default_rng(0).random((40, 50))
    fig, ax = plot_spectrogram(f, t, Sxx, percentile=95, band=[0.5, 30], color_bar=True)
    import matplotlib.pyplot as plt

    plt.close(fig)
    with pytest.raises(TypeError):
        plot_spectrogram(f, t, Sxx, percentile="x")


def test_plot_hypno(mianno):
    fig, ax = plot_hypno(mianno.sleep_state)
    import matplotlib.pyplot as plt

    plt.close(fig)
    with pytest.raises(TypeError):
        plot_hypno("not-a-list")


def test_config_defaults():
    cfg = load_config()
    assert "gui" in cfg.sections()
    assert "spec" in cfg.sections()
    assert cfg["gui"]["version"].startswith("v")
    assert float(cfg["spec"]["win_length_sec"]) > 0


def test_config_default_path_exists():
    assert default_config_path().exists()


def test_config_save_load(fresh_config, tmp_path):
    fresh_config.set("gui", "openpath", str(tmp_path))
    path = save_config(fresh_config)
    assert path.exists()
    reloaded = load_config(path=path)
    assert reloaded["gui"]["openpath"] == str(tmp_path)
