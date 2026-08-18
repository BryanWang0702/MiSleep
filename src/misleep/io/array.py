# -*- coding: UTF-8 -*-
"""Portable NumPy and delimited-text signal formats.

Plain arrays do not contain sampling frequency or acquisition-time metadata.
MiSleep therefore uses a small JSON sidecar next to ``.npy``, ``.csv`` and
``.tsv`` files.  For ``recording.npy`` either ``recording.npy.json`` (preferred)
or ``recording.json`` is accepted::

    {"sf": 256, "channels": ["EEG", "EMG"],
     "time": "20240409-18:00:00", "channel_axis": 0}

``.npz`` is self-contained and is the recommended NumPy interchange format.
Loading never enables NumPy pickle support, so untrusted files cannot execute
Python objects.
"""

from __future__ import annotations

import datetime as _datetime
import json
from pathlib import Path

import numpy as np

from misleep.data import MiData
from misleep.io.base import register_signal_reader, register_signal_writer

_TIME_FORMAT = "%Y%m%d-%H:%M:%S"


def _default_time(path: Path) -> str:
    """Use the file modification time when acquisition time is unavailable."""
    return _datetime.datetime.fromtimestamp(path.stat().st_mtime).strftime(_TIME_FORMAT)


def _read_sidecar(path: Path) -> dict:
    candidates = (path.with_suffix(path.suffix + ".json"), path.with_suffix(".json"))
    for candidate in candidates:
        if candidate.is_file():
            try:
                value = json.loads(candidate.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise ValueError(f"Invalid metadata sidecar {candidate}: {exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"Metadata sidecar {candidate} must contain a JSON object")
            return value
    return {}


def _metadata_list(value, count: int, name: str, cast):
    if np.isscalar(value):
        values = [cast(value)] * count
    else:
        values = [cast(item) for item in value]
    if len(values) != count:
        raise ValueError(f"'{name}' has {len(values)} values for {count} signal channels")
    return values


def _to_signals(array, metadata: dict, path: Path):
    data = np.asarray(array)
    if data.dtype.kind not in "biufc":
        raise ValueError(f"{path.name} must contain a numeric array, got dtype {data.dtype}")
    data = np.squeeze(data)
    if data.ndim == 1:
        signals = [np.asarray(data)]
    elif data.ndim == 2:
        channel_axis = metadata.get("channel_axis")
        if channel_axis is None:
            channel_axis = 0 if data.shape[0] <= data.shape[1] else 1
        if channel_axis not in (0, 1):
            raise ValueError("'channel_axis' must be 0 or 1")
        if channel_axis == 1:
            data = data.T
        signals = [np.asarray(row) for row in data]
    else:
        raise ValueError(
            f"{path.name} must be a 1-D or 2-D signal array; got shape {data.shape}")
    return signals


def _build_midata(array, metadata: dict, path: Path) -> MiData:
    if isinstance(array, list) and array and all(np.asarray(item).ndim == 1 for item in array):
        signals = [np.asarray(item) for item in array]
        if any(signal.dtype.kind not in "biufc" for signal in signals):
            raise ValueError(f"{path.name} contains a non-numeric signal array")
    else:
        signals = _to_signals(array, metadata, path)
    if any(signal.size == 0 for signal in signals):
        raise ValueError(f"{path.name} contains an empty signal channel")
    count = len(signals)
    if "sf" not in metadata:
        raise ValueError(
            f"Sampling frequency is missing for {path.name}. Add 'sf' to "
            f"{path.name}.json (for example: {{\"sf\": 256}}).")
    sf = _metadata_list(metadata["sf"], count, "sf", float)
    channels = metadata.get("channels", [f"ch{i + 1}" for i in range(count)])
    channels = _metadata_list(channels, count, "channels", str)
    time = str(metadata.get("time") or _default_time(path))
    try:
        _datetime.datetime.strptime(time, _TIME_FORMAT)
    except ValueError as exc:
        raise ValueError(f"'time' must use YYYYMMDD-HH:MM:SS, got {time!r}") from exc
    return MiData(signals=signals, channels=channels, sf=sf, time=time,
                  describe=str(metadata.get("describe", "")))


def load_npy(data_path) -> MiData:
    """Load a numeric ``.npy`` array plus its JSON metadata sidecar."""
    path = Path(data_path)
    try:
        array = np.load(path, allow_pickle=False)
    except ValueError as exc:
        raise ValueError(
            "Object/pickled NPY files are intentionally not loaded for security. "
            "Use a numeric array with a JSON sidecar, or the self-contained NPZ format."
        ) from exc
    return _build_midata(array, _read_sidecar(path), path)


def load_npz(data_path) -> MiData:
    """Load MiSleep's safe, self-contained ``.npz`` interchange format."""
    path = Path(data_path)
    try:
        archive = np.load(path, allow_pickle=False)
        with archive:
            keys = set(archive.files)
            metadata = _read_sidecar(path)
            for key in ("channels", "sf", "time", "describe", "channel_axis"):
                if key in keys:
                    value = archive[key]
                    metadata[key] = value.item() if value.ndim == 0 else value.tolist()
            signal_keys = sorted(
                (key for key in keys if key.startswith("signal_")),
                key=lambda key: int(key.split("_", 1)[1]),
            )
            if signal_keys:
                signals = [np.asarray(archive[key]) for key in signal_keys]
            elif "signals" in keys:
                signals = _to_signals(archive["signals"], metadata, path)
            else:
                numeric = [key for key in archive.files
                           if key not in {"sf", "channel_axis"}
                           and np.asarray(archive[key]).dtype.kind in "biufc"]
                if len(numeric) != 1:
                    raise ValueError(
                        "NPZ must contain 'signals', signal_0/signal_1 arrays, "
                        "or exactly one numeric array")
                signals = _to_signals(archive[numeric[0]], metadata, path)
    except (OSError, ValueError, TypeError) as exc:
        if isinstance(exc, ValueError) and "NPZ must" in str(exc):
            raise
        raise ValueError(f"Could not read NPZ signal file {path}: {exc}") from exc
    return _build_midata(signals, metadata, path)


def _load_delimited(data_path, separator: str) -> MiData:
    import pandas as pd

    path = Path(data_path)
    frame = pd.read_csv(path, sep=separator)
    if frame.empty:
        raise ValueError(f"Signal table {path} is empty")
    metadata = _read_sidecar(path)
    time_column = next(
        (name for name in frame.columns
         if str(name).strip().lower() in {"time", "times", "second", "seconds", "timestamp"}),
        None,
    )
    if time_column is not None and "sf" not in metadata:
        time_values = pd.to_numeric(frame.pop(time_column), errors="raise").to_numpy()
        steps = np.diff(time_values)
        steps = steps[np.isfinite(steps) & (steps > 0)]
        if not len(steps):
            raise ValueError("Time column must contain increasing values to infer sampling frequency")
        metadata["sf"] = float(1.0 / np.median(steps))
    numeric = frame.apply(pd.to_numeric, errors="raise")
    metadata.setdefault("channels", [str(name) for name in numeric.columns])
    metadata["channel_axis"] = 1
    return _build_midata(numeric.to_numpy(), metadata, path)


def load_csv(data_path) -> MiData:
    """Load a headered CSV; infer frequency from a time column if present."""
    return _load_delimited(data_path, ",")


def load_tsv(data_path) -> MiData:
    """Load a headered tab-separated signal table."""
    return _load_delimited(data_path, "\t")


def write_npz(signals, channels, sf, time, npz_file) -> None:
    """Write a pickle-free, self-contained NumPy archive."""
    payload = {f"signal_{i}": np.asarray(signal) for i, signal in enumerate(signals)}
    payload.update(channels=np.asarray(channels, dtype=str), sf=np.asarray(sf, dtype=float),
                   time=np.asarray(str(time)))
    np.savez_compressed(npz_file, **payload)


for _extension, _reader in {
    ".npy": load_npy,
    ".npz": load_npz,
    ".csv": load_csv,
    ".tsv": load_tsv,
}.items():
    register_signal_reader(_extension, _reader)

register_signal_writer(".npz", write_npz)
