# -*- coding: UTF-8 -*-
"""Fast multi-channel feature extraction for rodent sleep staging.

Vendored and adapted from the rodent-autostage benchmark pipeline:

* the feature window ``W`` slides every ``stride`` seconds (default 1 s) so
  state-transition edges are captured at 1 s resolution, while the epoch
  unit remains 5 s;
* a single **STFT** provides all spectral band powers and EEG-EMG
  coherence; rolling cumsum statistics provide the time-domain features;
  permutation entropy is vectorised on a decimated signal.

Channel roles are passed explicitly (``eeg`` / ``emg`` / ``acc``) together
with the EEG electrode site, which decides the feature prefixes:

* ``eegf_*`` (frontal) or ``eegp_*`` (parietal) for the EEG channel,
* ``emg_*`` for EMG, ``acc_*`` for ACC,
* ``cohf_*`` / ``cohp_*`` for EEG-EMG coherence (site-dependent).
"""

from __future__ import annotations

from math import factorial, log2

import numpy as np
from scipy import signal

EEG_BANDS = {"delta": (0.5, 4.0), "theta": (4.0, 8.0), "sigma": (10.0, 15.0),
             "beta": (15.0, 30.0), "gamma": (30.0, 50.0)}
EMG_BANDS = {"low": (10.0, 20.0), "high": (20.0, 50.0), "vhigh": (50.0, 100.0)}
ACC_BANDS = {"slow": (0.5, 2.0), "motion": (2.0, 10.0)}
COH_BANDS = {"delta": (0.5, 4.0), "theta": (4.0, 8.0), "sigma": (10.0, 15.0)}


# --------------------------------------------------------------------------
# filtering
# --------------------------------------------------------------------------

def _bandpass(sig, fs, low, high, order=4):
    ny = 0.5 * fs
    high = min(high, ny * 0.99)
    low = max(low, 0.1)
    if low >= high:
        return sig
    b, a = signal.butter(order, [low / ny, high / ny], btype="band")
    return signal.filtfilt(b, a, sig)


def _bandstop(sig, fs, low, high, order=4):
    ny = 0.5 * fs
    b, a = signal.butter(order, [low / ny, high / ny], btype="bandstop")
    return signal.filtfilt(b, a, sig)


def filter_signal(sig, fs, kind):
    """Band-pass a channel according to its type (eeg / emg / acc)."""
    sig = np.asarray(sig, dtype=np.float64)
    if kind == "eeg":
        out = _bandpass(sig, fs, 0.5, 40.0)
        out = _bandstop(out, fs, 47, 53)   # power-line notch
    elif kind == "emg":
        out = _bandpass(sig, fs, 10.0, 100.0)
    elif kind == "acc":
        out = _bandpass(sig, fs, 0.5, 20.0)
    else:
        out = sig
    return out


def filter_channels(sig_map, sf):
    """Band-pass every channel once. Returns {name: filtered_array}."""
    filtered = {}
    for name, sig in sig_map.items():
        kind = ("eeg" if name.upper().startswith("EEG")
                else ("emg" if "EMG" in name.upper()
                      else ("acc" if name.upper() == "ACC" else "other")))
        filtered[name] = filter_signal(sig, sf, kind)
    return filtered


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def _rolling_mean(x, n):
    """Mean of every n consecutive samples; length = len(x) - n + 1."""
    x = np.asarray(x)
    if n <= 1:
        return x
    c = np.cumsum(np.insert(x, 0, 0.0))
    return (c[n:] - c[:-n]) / n


# --------------------------------------------------------------------------
# spectral (STFT-based)
# --------------------------------------------------------------------------

def stft_band_powers(x, fs, bands, W, stride, nperseg=None, hop=None):
    """Relative band powers from a single STFT, rolling-averaged over W s."""
    nperseg = nperseg or int(fs * 2.0)
    hop = hop or int(fs * stride)
    f, t, Z = signal.stft(x, fs=fs, nperseg=nperseg, noverlap=nperseg - hop,
                          boundary=None, padded=False)
    P = np.abs(Z) ** 2
    total = P.sum(axis=0) + 1e-12
    n_cols_per_W = max(1, int(round(W * fs / hop)))
    out = {}
    for name, (lo, hi) in bands.items():
        idx = (f >= lo) & (f <= hi)
        pband = P[idx].sum(axis=0)
        out[name] = _rolling_mean(pband, n_cols_per_W) / _rolling_mean(total, n_cols_per_W)
    return out, f, Z


def stft_coherence(Zx, Zy, f, bands, W, stride, hop=None, fs=None):
    """EEG-EMG coherence per band from two STFTs, rolling-averaged over W s."""
    hop = hop or int(fs * stride)
    n_cols_per_W = max(1, int(round(W * fs / hop)))
    Pxx = np.abs(Zx) ** 2
    Pyy = np.abs(Zy) ** 2
    Pxy = Zx * np.conj(Zy)
    out = {}
    for name, (lo, hi) in bands.items():
        idx = (f >= lo) & (f <= hi)
        num = np.abs(_rolling_mean(Pxy[idx].sum(axis=0), n_cols_per_W)) ** 2
        den = _rolling_mean(Pxx[idx].sum(axis=0), n_cols_per_W) * \
              _rolling_mean(Pyy[idx].sum(axis=0), n_cols_per_W) + 1e-12
        out[name] = num / den
    return out


# --------------------------------------------------------------------------
# time-domain (rolling cumsum)
# --------------------------------------------------------------------------

def time_domain_features(x, fs, W, stride, include_shape=True):
    """Rolling time-domain features over a W-second window at ``stride`` step."""
    n_stride = int(fs * stride)
    win = int(fs * W)
    x = np.asarray(x, dtype=np.float64)
    N = len(x)

    c1 = np.cumsum(x)
    c2 = np.cumsum(x * x)
    dx = np.diff(x, prepend=x[0])
    adx = np.abs(dx)
    cadx = np.cumsum(adx)
    ddx = np.diff(dx, prepend=dx[0])
    cdx2 = np.cumsum(dx * dx)
    cddx2 = np.cumsum(ddx * ddx)
    sc = np.zeros(N, dtype=np.float64)
    sc[1:] = (np.signbit(x[1:]) != np.signbit(x[:-1])).astype(np.float64)
    csc = np.cumsum(sc)

    ends = np.arange(n_stride, N + 1, n_stride)  # exclusive end samples
    starts = np.maximum(0, ends - win)
    n_win = (ends - starts).astype(np.float64)

    def _diff(c):
        return (c[ends - 1] - np.where(starts == 0, 0.0, c[starts - 1]))

    s1 = _diff(c1)
    s2 = _diff(c2)
    mean = s1 / n_win
    var = np.maximum(s2 / n_win - mean ** 2, 0.0)
    std = np.sqrt(var)

    out = {}
    out["std"] = std
    out["line_len"] = _diff(cadx) / n_win
    out["zc"] = _diff(csc) / n_win

    vdx = _diff(cdx2) / n_win
    vddx = _diff(cddx2) / n_win
    mob = np.sqrt(vdx / np.maximum(var, 1e-12))
    comp = np.sqrt(vddx / np.maximum(vdx, 1e-12)) / np.maximum(mob, 1e-12)
    out["hj_mob"] = mob
    out["hj_comp"] = comp

    if include_shape:
        c3 = np.cumsum(x ** 3)
        c4 = np.cumsum(x ** 4)
        m3 = _diff(c3) / n_win
        m4 = _diff(c4) / n_win
        centered = mean
        mu3 = m3 - 3 * centered * (s2 / n_win) + 2 * centered ** 3
        mu4 = m4 - 4 * centered * m3 + 6 * centered ** 2 * (s2 / n_win) - 3 * centered ** 4
        out["skew"] = mu3 / np.maximum(std ** 3, 1e-12)
        out["kurt"] = mu4 / np.maximum(var ** 2, 1e-12) - 3.0

    out["rms"] = np.sqrt(s2 / n_win)
    out["log_power"] = np.log10(np.maximum(s2, 1e-12))
    return out


def perm_entropy_series(x, fs, stride, W, decim=16, m=3, tau=1):
    """Per-stride permutation entropy over a W-second window (decimated)."""
    xd = np.asarray(x[::decim], dtype=np.float64)
    n_stride = max(1, int(round(fs * stride / decim)))
    n_win = int(round(fs * W / decim))
    if len(xd) < n_win:
        return np.zeros(0)
    from numpy.lib.stride_tricks import sliding_window_view
    win = sliding_window_view(xd, n_win)[::n_stride]  # (T, n_win)
    T = win.shape[0]
    if T == 0:
        return np.zeros(0)
    sub = sliding_window_view(win, m * tau, axis=1)[:, ::tau]  # (T, K, m)
    order = np.argsort(sub, axis=2)
    code = order[:, :, 0] * (m * m) + order[:, :, 1] * m + order[:, :, 2]
    n_bins = m ** m
    T_, K = code.shape
    flat = code + np.arange(T_)[:, None] * n_bins
    counts = np.bincount(flat.ravel(), minlength=T_ * n_bins).reshape(T_, n_bins)
    n_subs = n_win - (m - 1) * tau
    probs = counts / n_subs
    pe = -np.sum(probs * np.log2(np.maximum(probs, 1e-12)), axis=1)
    return pe / log2(factorial(m))


# --------------------------------------------------------------------------
# channel feature builders
# --------------------------------------------------------------------------

def _eeg_channel(x, fs, W, stride, band_powers, tfeats):
    f = {}
    f["std"] = tfeats["std"]
    f["line_len"] = tfeats["line_len"]
    f["zc"] = tfeats["zc"]
    f["hj_mob"] = tfeats["hj_mob"]
    f["hj_comp"] = tfeats["hj_comp"]
    f["skew"] = tfeats["skew"]
    f["kurt"] = tfeats["kurt"]
    f["perm_ent"] = perm_entropy_series(x, fs, stride, W)
    for k in ["delta", "theta", "sigma", "beta", "gamma"]:
        f[k] = band_powers[k]
    d = band_powers["delta"] + 1e-12
    t = band_powers["theta"] + 1e-12
    f["delta_theta"] = d / t
    f["theta_delta"] = t / d
    f["delta_sigma"] = d / (band_powers["sigma"] + 1e-12)
    f["slow_fast"] = (d + t) / (band_powers["beta"] + band_powers["gamma"] + 1e-12)
    return f


def _emg_channel(x, fs, W, stride, band_powers, tfeats):
    f = {}
    f["std"] = tfeats["std"]
    f["rms"] = tfeats["rms"]
    f["zc"] = tfeats["zc"]
    f["hj_mob"] = tfeats["hj_mob"]
    f["hj_comp"] = tfeats["hj_comp"]
    f["perm_ent"] = perm_entropy_series(x, fs, stride, W)
    f["line_len"] = tfeats["line_len"]
    for k in ["low", "high", "vhigh"]:
        f[k] = band_powers[k]
    f["log_power"] = tfeats["log_power"]
    return f


def _acc_channel(x, fs, W, stride, band_powers, tfeats):
    f = {}
    f["std"] = tfeats["std"]
    f["rms"] = tfeats["rms"]
    f["zc"] = tfeats["zc"]
    f["hj_mob"] = tfeats["hj_mob"]
    f["perm_ent"] = perm_entropy_series(x, fs, stride, W)
    f["line_len"] = tfeats["line_len"]
    for k in ["slow", "motion"]:
        f[k] = band_powers[k]
    f["log_power"] = tfeats["log_power"]
    return f


# --------------------------------------------------------------------------
# top-level extraction (explicit channel roles + EEG site)
# --------------------------------------------------------------------------

def extract_fast(filtered, sf, W=10.0, stride=1.0, return_seconds=False):
    """Extract all features from *pre-filtered* channels at ``stride`` resolution.

    ``filtered`` : dict {channel_name: array} with the selected channels
    already renamed to ``EEG_F`` / ``EEG_P`` (site-dependent), ``EMG`` and
    ``ACC``. Returns dict with 'X' (T, n_feat), 'feature_names', and
    optionally 'seconds' (start second of each window).
    """
    nperseg = int(sf * 2.0)
    hop = int(sf * stride)

    spec = {}
    Zs = {}
    f_axis = None
    for name in filtered:
        kind = ("eeg" if name.upper().startswith("EEG")
                else ("emg" if "EMG" in name.upper()
                      else ("acc" if name.upper() == "ACC" else None)))
        if kind is None:
            continue
        bands = EEG_BANDS if kind == "eeg" else (EMG_BANDS if kind == "emg" else ACC_BANDS)
        bp, f_axis, Z = stft_band_powers(filtered[name], sf, bands, W, stride,
                                         nperseg=nperseg, hop=hop)
        spec[name] = (kind, bp)
        Zs[name] = Z

    # coherence (EEG site x EMG)
    coh = {}
    emg_name = next((n for n in filtered if "EMG" in n.upper()), None)
    for name in filtered:
        if name.upper().startswith("EEG") and emg_name is not None and emg_name in Zs:
            coh[name] = stft_coherence(Zs[name], Zs[emg_name], f_axis, COH_BANDS,
                                       W, stride, hop=hop, fs=sf)

    # time-domain per channel
    td = {}
    for name in filtered:
        kind = ("eeg" if name.upper().startswith("EEG")
                else ("emg" if "EMG" in name.upper()
                      else ("acc" if name.upper() == "ACC" else None)))
        if kind is None:
            continue
        td[name] = time_domain_features(filtered[name], sf, W, stride,
                                        include_shape=(kind == "eeg"))

    def _stack(feats):
        keys = sorted(feats.keys())
        n = min(feats[k].shape[0] for k in keys)
        return np.column_stack([feats[k][:n] for k in keys]), keys

    col_names, cols = [], []
    for name in ["EEG_F", "EEG_P"]:
        if name in spec:
            kind, bp = spec[name]
            feats = _eeg_channel(filtered[name], sf, W, stride, bp, td[name])
            prefix = "eegf" if name == "EEG_F" else "eegp"
            arr, keys = _stack(feats)
            cols.append(arr)
            col_names += [f"{prefix}_{k}" for k in keys]
    for name in ["EMG"]:
        if name in spec:
            _, bp = spec[name]
            feats = _emg_channel(filtered[name], sf, W, stride, bp, td[name])
            arr, keys = _stack(feats)
            cols.append(arr)
            col_names += [f"emg_{k}" for k in keys]
    for name in ["ACC"]:
        if name in spec:
            _, bp = spec[name]
            feats = _acc_channel(filtered[name], sf, W, stride, bp, td[name])
            arr, keys = _stack(feats)
            cols.append(arr)
            col_names += [f"acc_{k}" for k in keys]
    for name in ["EEG_F", "EEG_P"]:
        if name in coh:
            prefix = "cohf" if name == "EEG_F" else "cohp"
            arr, keys = _stack(coh[name])
            cols.append(arr)
            col_names += [f"{prefix}_{k}" for k in keys]

    if not cols:
        return {"X": np.zeros((0, 0)), "feature_names": []}
    n = min(c.shape[0] for c in cols)
    cols = [c[:n] for c in cols]
    X = np.column_stack(cols) if cols else np.zeros((0, 0))

    out = {"X": X, "feature_names": col_names}
    if return_seconds:
        out["seconds"] = (np.arange(n) * stride + W).astype(np.float64)
    return out
