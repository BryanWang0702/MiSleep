# -*- coding: UTF-8 -*-
"""Tests for preprocessing: filtering, artifacts and spectral analysis."""

import numpy as np
import pytest

from misleep.preprocessing.artifacts import reject_artifact, z_score
from misleep.preprocessing.filtering import filter_power_line_noise, signal_filter
from misleep.preprocessing.spectral import band_power, spectrogram, spectrum


def test_signal_filter_types():
    data = np.random.default_rng(0).standard_normal(256 * 10)
    with pytest.raises(TypeError):
        signal_filter(data, sf="x")
    with pytest.raises(ValueError):
        signal_filter(data, sf=256, btype="not_a_filter")


def test_signal_filter_bandpass_removes_out_of_band():
    sf = 256.0
    t = np.arange(sf * 20) / sf
    signal = np.sin(2 * np.pi * 2 * t) + np.sin(2 * np.pi * 60 * t)
    filtered, fname = signal_filter(signal, sf=sf, btype="bandpass", low=0.5, high=30)
    assert fname == "bandpass_0.5_30"
    # 60 Hz component should be strongly attenuated
    freqs = np.fft.rfftfreq(len(filtered), 1 / sf)
    spec = np.abs(np.fft.rfft(filtered))
    idx_60 = np.argmin(np.abs(freqs - 60))
    idx_2 = np.argmin(np.abs(freqs - 2))
    assert spec[idx_60] < spec[idx_2]


def test_filter_power_line_noise():
    sf = 256.0
    t = np.arange(sf * 10) / sf
    signal = np.sin(2 * np.pi * 50 * t) + np.sin(2 * np.pi * 3 * t)
    cleaned = filter_power_line_noise(signal, sf=sf)
    freqs = np.fft.rfftfreq(len(cleaned), 1 / sf)
    spec = np.abs(np.fft.rfft(cleaned))
    idx_50 = np.argmin(np.abs(freqs - 50))
    idx_3 = np.argmin(np.abs(freqs - 3))
    assert spec[idx_50] < spec[idx_3]


def test_z_score():
    data = np.arange(10, dtype=float)
    z = z_score(data)
    assert np.allclose(z.mean(), 0)
    assert np.allclose(z.std(), 1)


def test_reject_artifact_removes_noise():
    sf = 256.0
    clean = np.random.default_rng(0).standard_normal(int(sf * 20)) * 0.1
    # Inject a huge artifact epoch in the middle
    noisy = clean.copy()
    noisy[int(sf * 10): int(sf * 15)] = np.random.default_rng(1).standard_normal(int(sf * 5)) * 50
    cleaned = reject_artifact(noisy, sf=sf, threshold=2)
    assert len(cleaned) < len(noisy)
    assert np.abs(cleaned).max() < 5


def test_spectrum(midata):
    freq, psd = spectrum(midata.signals[0], midata.sf[0], band=[0.5, 30], relative=True)
    assert freq[0] >= 0.5 and freq[-1] <= 30
    assert np.all(psd >= 0)
    # Exact band endpoints can add nonuniform intervals; use the same
    # integration rule as relative normalization.
    from scipy.integrate import simpson
    assert np.isclose(simpson(psd, x=freq), 1.0)


def test_spectrum_validation():
    with pytest.raises(TypeError):
        spectrum([1, 2, 3], 256)
    with pytest.raises(TypeError):
        spectrum(np.zeros(100), "x")


def test_fractional_sample_rate_spectral_boundaries():
    """A 30.009 Hz FFT bin must not make the 30 Hz endpoint disappear."""
    from scipy.signal import welch
    from misleep.gui.qt_utils import cal_draw_spectrum

    sf = 100.03
    signal = np.random.default_rng(12).standard_normal(4000)
    raw_freq, raw_power = welch(signal, sf, nperseg=1000)
    spec, figure = cal_draw_spectrum(
        signal, sf, nperseg=1000, freq_band=[0.5, 30], relative=False)
    assert spec[0, 0] == 0.5
    assert spec[0, -1] == 30.0
    assert np.all(np.diff(spec[0]) > 0)
    np.testing.assert_allclose(
        spec[1, [0, -1]], np.interp([0.5, 30], raw_freq, raw_power))
    # Interior bins retain their actual frequencies, rather than 2-digit labels.
    np.testing.assert_array_equal(
        spec[0, 1:-1], raw_freq[(raw_freq > 0.5) & (raw_freq < 30)])
    figure.clear()

    freq, power = spectrum(
        signal, sf, band=[0.5, 30], win_sec=10, relative=False)
    assert freq[0] == 0.5 and freq[-1] == 30
    assert len(freq) == len(power)
    freq, times, power = spectrogram(
        signal, sf, band=[0.5, 30], win_sec=10, step=1)
    assert freq[0] == 0.5 and freq[-1] == 30
    assert power.shape == (len(freq), len(times))


def test_spectral_band_power_interpolates_boundaries():
    from misleep.preprocessing.spectral import _select_frequency_band

    freq = np.array([0.0, 1.0003, 2.0006, 3.0009])
    power = 2 * freq + 1
    selected, values = _select_frequency_band(freq, power, [0.5, 3.0])
    assert selected[0] == 0.5 and selected[-1] == 3.0
    np.testing.assert_allclose(values, 2 * selected + 1)
    assert band_power(power, freq, [[0.5, 3.0, "band"]])["band"] == pytest.approx(11.25)
    # No extrapolation past Nyquist, and aligned bins are not duplicated.
    selected, _ = _select_frequency_band(freq, power, [0.0, 4.0])
    np.testing.assert_array_equal(selected, freq)


def test_spectrogram(midata):
    f, t, Sxx = spectrogram(midata.signals[0], midata.sf[0], band=[0.5, 30], step=1, win_sec=2)
    assert f.shape[0] == Sxx.shape[0]
    assert t.shape[0] == Sxx.shape[1]
    assert np.all(Sxx >= 0)


def test_spectrogram_validation():
    with pytest.raises(ValueError):
        spectrogram(np.zeros(1000), 256, step=5, win_sec=2)  # step > win_sec


def test_band_power(midata):
    freq, psd = spectrum(midata.signals[0], midata.sf[0], band=[0.5, 30], relative=False)
    bp = band_power(psd, freq, bands=[[0.5, 4, "delta"], [4, 9, "theta"]])
    assert set(bp.keys()) == {"delta", "theta"}
    assert bp["delta"] > 0 and bp["theta"] > 0
