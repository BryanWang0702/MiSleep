from __future__ import annotations

from typing import Optional, Sequence, Tuple

import numpy as np
from scipy import signal

from .configs import PreprocessConfig


def design_bandpass_sos(low_cut: float, high_cut: float, sample_rate: float, order: int) -> np.ndarray:
    return signal.butter(order, [low_cut, high_cut], btype="bandpass",
                         fs=sample_rate, output="sos")


def build_channel_filters(cfg: PreprocessConfig) -> Tuple[np.ndarray, np.ndarray]:
    eeg_low, eeg_high = cfg.eeg_band
    emg_low, emg_high = cfg.emg_band
    eeg_sos = design_bandpass_sos(eeg_low, eeg_high, cfg.sample_rate, cfg.filter_order)
    emg_sos = design_bandpass_sos(emg_low, emg_high, cfg.sample_rate, cfg.filter_order)
    return eeg_sos, emg_sos


def apply_bandpass(signal_arr: np.ndarray, sos_filters: Sequence[np.ndarray],
                   real_time: bool = False) -> np.ndarray:
    """
    Band-pass filter a multi-channel signal.

    Parameters
    ----------
    signal_arr : ndarray
        Shape ``(channels, samples)``.
    sos_filters : sequence of ndarray
        One SOS filter per channel (the last filter is reused if fewer are given).
    real_time : bool
        When True, applies causal filtering (``sosfilt``) to emulate online
        processing; otherwise zero-phase ``sosfiltfilt`` is used.
    """
    if len(sos_filters) == 0:
        raise ValueError("At least one SOS filter must be provided.")
    filtered = np.empty_like(signal_arr, dtype=np.float32)
    filter_fn = signal.sosfilt if real_time else signal.sosfiltfilt
    for ch in range(signal_arr.shape[0]):
        sos = sos_filters[min(ch, len(sos_filters) - 1)]
        filtered[ch] = filter_fn(sos, signal_arr[ch].astype(np.float32))
    return filtered


def exponential_moving_standardize(
    signal_arr: np.ndarray,
    alpha: float = 0.999,
    init_window: Optional[int] = None,
) -> np.ndarray:
    """
    Exponential moving standardization applied per channel.

    ``x'_k = (x_k - mu_k) / sqrt(sigma_k^2)`` with
    ``mu_k = (1 - alpha) * x_k + alpha * mu_{k-1}`` and
    ``sigma_k^2 = (1 - alpha) * (x_k - mu_k)^2 + alpha * sigma_{k-1}^2``.
    """
    if signal_arr.ndim != 2:
        raise ValueError("Signal array must have shape (channels, samples) for standardization.")
    channels, samples = signal_arr.shape
    standardized = np.empty_like(signal_arr, dtype=np.float32)
    window = samples if init_window is None else max(1, min(samples, int(init_window)))
    init_slice = signal_arr[:, :window]
    mu = init_slice.mean(axis=1, keepdims=True).astype(np.float32)
    var = init_slice.var(axis=1, keepdims=True).astype(np.float32)
    var = np.clip(var, 1e-6, None)
    for idx in range(samples):
        x = signal_arr[:, idx: idx + 1].astype(np.float32)
        mu = (1.0 - alpha) * x + alpha * mu
        var = (1.0 - alpha) * (x - mu) ** 2 + alpha * var
        std = np.sqrt(np.maximum(var, 1e-6))
        standardized[:, idx] = ((x - mu) / std)[:, 0]
    return standardized


def epoch_signal(signal_arr: np.ndarray, cfg: PreprocessConfig) -> np.ndarray:
    """Slice a signal into non-overlapping epochs of ``cfg.epoch_seconds``."""
    c, total = signal_arr.shape
    samples_per_epoch = cfg.samples_per_epoch()
    hop = cfg.hop_length_samples()
    if total < samples_per_epoch:
        return np.zeros((0, c, samples_per_epoch), dtype=np.float32)
    epochs = []
    start = 0
    while start + samples_per_epoch <= total:
        epochs.append(signal_arr[:, start: start + samples_per_epoch])
        start += hop
    if not epochs:
        return np.zeros((0, c, samples_per_epoch), dtype=np.float32)
    return np.stack(epochs, axis=0).astype(np.float32)


def augment_epoch(
    epoch: np.ndarray,
    scale_range: Tuple[float, float] = (0.9, 1.1),
    noise_std_ratio: float = 0.02,
) -> np.ndarray:
    """Light data augmentation (scaling + Gaussian noise) for one epoch."""
    scaled = epoch * np.random.uniform(*scale_range)
    noise_std = noise_std_ratio * np.std(scaled, axis=-1, keepdims=True)
    noise = np.random.randn(*scaled.shape).astype(np.float32) * noise_std
    return scaled + noise
