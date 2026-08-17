from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import torch
from torch.utils.data import Dataset

from .configs import PreprocessConfig
from .preprocessing import (
    apply_bandpass,
    augment_epoch,
    build_channel_filters,
    epoch_signal,
    exponential_moving_standardize,
)


def _resolve_mat_key(mat_dict: Dict) -> str:
    keys = [k for k in mat_dict.keys() if not k.startswith("__")]
    if not keys:
        raise ValueError("MAT file does not contain any usable keys.")
    if len(keys) == 1:
        return keys[0]
    for candidate in keys:
        if candidate.lower().startswith("mouse"):
            return candidate
    return keys[0]


def _extract_sample_rate(entry: Dict, default: float) -> float:
    for key in ("sf", "fs", "sample_rate"):
        if key not in entry:
            continue
        try:
            values = np.asarray(entry[key], dtype=np.float32).ravel()
        except Exception:
            continue
        for val in values:
            if val > 0:
                return float(val)
    return float(default)


def load_mouse_recording(
    data_path: Path,
    *,
    return_sample_rate: bool = False,
    default_sample_rate: float = 305.1758,
) -> np.ndarray | Tuple[np.ndarray, float]:
    """Load a raw ``(2, samples)`` EEG/EMG recording from ``.mat`` or ``.edf``."""
    if str(data_path).endswith(".mat"):
        import scipy.io as sio

        data_ = sio.loadmat(data_path, simplify_cells=True)
        key = data_path.stem if data_path.stem in data_ else _resolve_mat_key(data_)
        entry = data_[key]
    elif str(data_path).endswith(".edf"):
        import misleep

        midata = misleep.load_edf(data_path)
        entry = {"EEG": midata.signals[0], "EMG_DIFF": midata.signals[1], "sf": midata.sf[0]}
    else:
        raise ValueError(f"Unsupported file type: {data_path}")

    sample_rate = _extract_sample_rate(entry, default_sample_rate)
    if "EEG_P" in entry:
        eeg_raw = entry["EEG_P"]
    elif "EEG" in entry:
        eeg_raw = entry["EEG"]
    else:
        raise KeyError(f"Missing EEG_P or EEG in {data_path}")
    eeg = np.asarray(eeg_raw, dtype=np.float32)
    emg = np.asarray(entry["EMG_DIFF"], dtype=np.float32)
    min_len = min(eeg.shape[-1], emg.shape[-1])
    if min_len <= 0:
        raise ValueError(f"Invalid recording length in {data_path}")
    if eeg.shape[-1] != min_len:
        eeg = eeg[..., :min_len]
    if emg.shape[-1] != min_len:
        emg = emg[..., :min_len]
    stacked = np.stack([eeg, emg], axis=0)
    if return_sample_rate:
        return stacked, sample_rate
    return stacked


def parse_label_file(txt_path: Path) -> Tuple[List[Dict], Dict]:
    """Parse a MiSleep annotation ``.txt`` into entries and metadata."""
    entries: List[Dict] = []
    base_seconds = None
    with txt_path.open("r", encoding="utf-8", errors="ignore") as f:
        lines = [line.strip() for line in f if line.strip()]
    parsing = False
    for line in lines:
        if line.startswith("==========Sleep stage"):
            parsing = True
            continue
        if not parsing:
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 8:
            continue
        start_code, start_idx, _, end_code, end_idx, _, label_id, label_name = parts[:8]
        entry = {
            "start_code": start_code,
            "end_code": end_code,
            "start_idx": int(start_idx),
            "end_idx": int(end_idx),
            "label_id": int(label_id),
            "label_name": label_name,
        }
        entries.append(entry)
        if base_seconds is None:
            day, hour, minute, second = (int(v) for v in start_code.split(":"))
            base_seconds = ((day * 24 + hour) * 60 + minute) * 60 + second
    meta = {"base_seconds": base_seconds or 0,
            "duration_units": entries[-1]["end_idx"] if entries else 0}
    return entries, meta


def build_label_array(num_samples: int, annotations: Sequence[Dict], samples_per_unit: float) -> np.ndarray:
    """Build a per-sample label array from parsed annotation entries."""
    labels = np.full(num_samples, -1, dtype=np.int16)
    id_map = {1: 0, 2: 1, 3: 2}  # NREM, REM, Wake
    for entry in annotations:
        start = max(0, int(round(entry["start_idx"] * samples_per_unit)))
        end = min(num_samples, int(round(entry["end_idx"] * samples_per_unit)))
        if end <= start:
            continue
        mapped = id_map.get(entry["label_id"], -1)
        if mapped >= 0:
            labels[start:end] = mapped
    return labels


def slice_epochs_with_labels(
    signal_arr: np.ndarray,
    labels: np.ndarray,
    cfg: PreprocessConfig,
    min_valid_ratio: float = 0.8,
) -> Tuple[np.ndarray, np.ndarray]:
    """Slice a signal into epochs and assign each epoch its majority label."""
    samples_per_epoch = cfg.samples_per_epoch()
    hop = cfg.hop_length_samples()
    total = signal_arr.shape[1]
    if total < samples_per_epoch:
        return (np.zeros((0, signal_arr.shape[0], samples_per_epoch), dtype=np.float32),
                np.zeros((0,), dtype=np.int64))
    usable_epochs: List[np.ndarray] = []
    epoch_labels: List[int] = []
    start = 0
    while start + samples_per_epoch <= total:
        end = start + samples_per_epoch
        epoch_signal_arr = signal_arr[:, start:end]
        label_slice = labels[start:end]
        valid = label_slice[label_slice >= 0]
        if valid.size / samples_per_epoch < min_valid_ratio:
            start += hop
            continue
        epoch_label = int(np.bincount(valid, minlength=3).argmax())
        usable_epochs.append(epoch_signal_arr)
        epoch_labels.append(epoch_label)
        start += hop
    if not usable_epochs:
        channels = signal_arr.shape[0]
        return (np.zeros((0, channels, samples_per_epoch), dtype=np.float32),
                np.zeros((0,), dtype=np.int64))
    return np.stack(usable_epochs), np.asarray(epoch_labels, dtype=np.int64)


@dataclass()
class SubjectEpochs:
    """Epochs and labels of one subject."""

    subject_id: str
    epochs: np.ndarray  # shape (N, 2, T)
    labels: np.ndarray  # shape (N,)


@dataclass()
class SubjectInfo:
    """Metadata of one subject."""

    subject_id: str  # relative path without extension
    data_path: Path
    label_path: Optional[Path]
    age_group: str
    mouse_id: str
    extension: str


class SleepEpochDataset(Dataset):
    """PyTorch dataset of context-window sequences with labels."""

    def __init__(self, subjects: Sequence[SubjectEpochs], window_size: int,
                 augment: bool = False) -> None:
        self.window = max(1, window_size)
        self.augment = augment
        self.samples: List[np.ndarray] = []
        self.labels: List[int] = []
        for subj in subjects:
            epochs = subj.epochs.astype(np.float32)
            labels = subj.labels.astype(np.int64)
            if epochs.size == 0:
                continue
            seqs, seq_labels = self._build_sequences(epochs, labels)
            self.samples.append(seqs)
            self.labels.append(seq_labels)

        if self.samples:
            lengths = [arr.shape[0] for arr in self.samples]
            self.offsets = np.cumsum([0] + lengths)
            self.flat_labels = np.concatenate(self.labels)
        else:
            self.offsets = np.array([0], dtype=np.int64)
            self.flat_labels = np.zeros((0,), dtype=np.int64)

    def _build_sequences(self, epochs: np.ndarray, labels: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        total = epochs.shape[0]
        seqs = []
        seq_labels = []
        for idx in range(total):
            start = max(0, idx - self.window + 1)
            seq = epochs[start: idx + 1]
            if seq.shape[0] < self.window:
                pad = np.repeat(seq[0:1], self.window - seq.shape[0], axis=0)
                seq = np.concatenate([pad, seq], axis=0)
            seqs.append(seq)
            seq_labels.append(labels[idx])
        return np.stack(seqs, axis=0), np.asarray(seq_labels, dtype=np.int64)

    def __len__(self) -> int:
        return int(self.offsets[-1])

    def _locate(self, idx: int) -> Tuple[int, int]:
        lo, hi = 0, len(self.offsets) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if idx < self.offsets[mid + 1]:
                hi = mid
            else:
                lo = mid + 1
        subj_idx = lo
        offset = idx - self.offsets[subj_idx]
        return subj_idx, offset

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        subj_idx, offset = self._locate(idx)
        seq = self.samples[subj_idx][offset]
        label = self.labels[subj_idx][offset]
        if self.augment:
            seq = np.stack([augment_epoch(epoch) for epoch in seq], axis=0)
        return torch.from_numpy(seq), torch.tensor(label, dtype=torch.long)


def _sanitize_subject_id(subject_id: str) -> str:
    return subject_id.replace("/", "__").replace("\\", "__")


def resolve_subject_paths(subject_id: str, data_dir: Path, data_format: str = "mat") -> Tuple[Path, Optional[Path]]:
    base = data_dir / subject_id
    if data_format == "mat":
        mat_path = Path(str(base) + ".mat")
        txt_path = Path(str(base) + ".txt")
        if not mat_path.exists():
            raise FileNotFoundError(f"MAT file not found for subject '{subject_id}' at {mat_path}")
        if not txt_path.exists():
            raise FileNotFoundError(f"TXT file not found for subject '{subject_id}' at {txt_path}")
        return mat_path, txt_path
    if data_format == "npy":
        npy_path = Path(str(base) + ".npz")
        if not npy_path.exists():
            raise FileNotFoundError(f"NPZ file not found for subject '{subject_id}' at {npy_path}")
        return npy_path, None
    raise ValueError(f"Unsupported data format '{data_format}'")


def discover_subject_infos(data_dir: Path, data_format: str = "mat") -> List[SubjectInfo]:
    """Discover ``.mat``/``.npz`` subjects (with label files) under a directory."""
    infos: List[SubjectInfo] = []
    if not data_dir.exists():
        return infos
    pattern = "*.npz" if data_format == "npy" else "*.mat"
    for data_file in sorted(data_dir.rglob(pattern)):
        if not data_file.is_file():
            continue
        if data_format == "mat":
            label_path = data_file.with_suffix(".txt")
            if not label_path.exists():
                continue
        else:
            label_path = None
        rel_path = data_file.relative_to(data_dir)
        rel_id = rel_path.with_suffix("").as_posix()
        parts = rel_path.parts
        if parts:
            age_group = parts[0]
            mouse_id = parts[-2] if len(parts) >= 2 else parts[0]
        else:
            age_group = "root"
            mouse_id = "root"
        infos.append(SubjectInfo(
            subject_id=rel_id,
            data_path=data_file,
            label_path=label_path,
            age_group=age_group,
            mouse_id=mouse_id,
            extension=data_file.suffix,
        ))
    return infos


def load_subject_epochs(
    subject_id: str,
    data_dir: Path,
    cfg: PreprocessConfig,
    cache_dir: Optional[Path] = None,
    data_format: str = "mat",
) -> SubjectEpochs:
    """Load (and optionally cache) the epochs + labels of one subject."""
    mat_path, txt_path = resolve_subject_paths(subject_id, data_dir, data_format=data_format)
    cache_file = None
    if cache_dir and data_format == "mat":
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = cache_dir / f"{_sanitize_subject_id(subject_id)}_epochs.npz"
        if cache_file.exists():
            data = np.load(cache_file)
            cached = SubjectEpochs(subject_id, data["epochs"], data["labels"])
            expected_len = cfg.samples_per_epoch()
            expected_hop = cfg.hop_length_samples()
            cache_len = int(data["epoch_samples"]) if "epoch_samples" in data else cached.epochs.shape[-1]
            cache_hop = int(data["hop_samples"]) if "hop_samples" in data else expected_hop + 1
            standardization = data["standardization"] if "standardization" in data else None
            if cache_len == expected_len and cache_hop == expected_hop and standardization == "exp_mov":
                return cached
            print(f"[Cache] {cache_file.name} mismatch detected; rebuilding with new preprocessing settings.")
    if data_format == "npy":
        data = np.load(mat_path)
        return SubjectEpochs(subject_id, data["epochs"], data["labels"])

    raw = load_mouse_recording(mat_path)
    annotations, meta = parse_label_file(txt_path)
    sos = build_channel_filters(cfg)
    filtered = apply_bandpass(raw, sos)
    standardized = exponential_moving_standardize(filtered, init_window=cfg.samples_per_epoch())
    samples_per_unit = raw.shape[1] / max(meta["duration_units"], 1)
    labels = build_label_array(raw.shape[1], annotations, samples_per_unit)
    epochs, epoch_labels = slice_epochs_with_labels(standardized, labels, cfg)

    if cache_file is not None:
        np.savez_compressed(
            cache_file,
            epochs=epochs,
            labels=epoch_labels,
            epoch_samples=cfg.samples_per_epoch(),
            hop_samples=cfg.hop_length_samples(),
            standardization="exp_mov",
        )
    return SubjectEpochs(subject_id, epochs, epoch_labels)
