from __future__ import annotations

from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

import numpy as np

from .configs import EEGTransformerConfig, PreprocessConfig
from .models import build_model
from .preprocessing import (
    apply_bandpass,
    build_channel_filters,
    epoch_signal,
    exponential_moving_standardize,
)


def default_checkpoint_path() -> Path:
    """Return the path of the packaged CausalTransformer checkpoint."""
    ref = files("misleep.analysis.transformer.checkpoints")
    return Path(str(ref)) / "CausalTransformer_best.pt"


@dataclass()
class AutoStageConfig:
    """
    Configuration for offline auto staging with the transformer models.

    Most users can leave this at the defaults and only set ``model_path``
    and ``sf``.
    """

    model_name: str = "CausalTransformer"
    model_path: Optional[Path] = None
    sf: float = 305.1758
    epoch_seconds: float = 5.0
    filter_order: int = 4
    eeg_band: Tuple[float, float] = (0.5, 30.0)
    emg_band: Tuple[float, float] = (15.0, 100.0)
    context_window: Optional[int] = None
    finetune_frac: float = 1.0
    finetune_epochs: int = 5
    finetune_lr: float = 5e-5
    finetune_batch: int = 16
    label_stride_seconds: float = 5.0
    label_mode: str = "stage_id"
    output_stride_seconds: float = 5.0
    output_label_mode: str = "stage_id"
    device: Optional[str] = None
    override_model_sample_rate: Optional[float] = None


def _validate_1d(arr: np.ndarray, name: str) -> np.ndarray:
    arr = np.asarray(arr).squeeze()
    if arr.ndim != 1:
        raise ValueError(f"{name} must be 1D after squeeze; got shape {arr.shape}")
    return arr.astype(np.float32)


def _map_label_value(value: int, mode: str) -> int:
    if mode == "stage_id":
        if value in (1, 2, 3):
            return value - 1
        return -1
    if mode == "class":
        if value in (0, 1, 2):
            return value
        return -1
    raise ValueError("label_mode must be 'stage_id' or 'class'")


def _labels_to_sample_labels(
    labels: Sequence[int],
    total_samples: int,
    sf: float,
    label_stride_seconds: float,
    label_mode: str,
) -> np.ndarray:
    sample_labels = np.full(total_samples, -1, dtype=np.int16)
    if not labels:
        return sample_labels
    samples_per_unit = int(round(sf * label_stride_seconds))
    if samples_per_unit <= 0:
        return sample_labels
    for idx, raw_label in enumerate(labels):
        mapped = _map_label_value(int(raw_label), label_mode)
        if mapped < 0:
            continue
        start = idx * samples_per_unit
        end = min(start + samples_per_unit, total_samples)
        if start >= total_samples:
            break
        sample_labels[start:end] = mapped
    return sample_labels


def _compute_epoch_labels(
    sample_labels: np.ndarray,
    cfg: PreprocessConfig,
    min_valid_ratio: float = 0.8,
) -> np.ndarray:
    samples_per_epoch = cfg.samples_per_epoch()
    hop = cfg.hop_length_samples()
    total = sample_labels.shape[0]
    if total < samples_per_epoch:
        return np.zeros((0,), dtype=np.int64)
    epoch_labels: List[int] = []
    start = 0
    while start + samples_per_epoch <= total:
        end = start + samples_per_epoch
        label_slice = sample_labels[start:end]
        valid = label_slice[label_slice >= 0]
        if valid.size / samples_per_epoch < min_valid_ratio:
            epoch_labels.append(-1)
        else:
            epoch_labels.append(int(np.bincount(valid, minlength=3).argmax()))
        start += hop
    return np.asarray(epoch_labels, dtype=np.int64)


def _prepare_sequences(
    epochs: np.ndarray,
    labels: np.ndarray,
    context_window: int,
) -> Tuple[np.ndarray, np.ndarray]:
    sequences: list[np.ndarray] = []
    seq_labels: list[int] = []
    buffer: list[np.ndarray] = []
    epoch_shape = epochs.shape[1:] if epochs.ndim >= 3 else ()
    for idx, epoch in enumerate(epochs):
        buffer.append(epoch)
        if len(buffer) > context_window:
            buffer.pop(0)
        seq = list(buffer)
        if len(seq) < context_window:
            seq = [seq[0]] * (context_window - len(seq)) + seq
        arr = np.stack(seq, axis=0)
        sequences.append(arr.astype(np.float32))
        seq_labels.append(int(labels[idx]))
    if not sequences:
        return np.empty((0, context_window, *epoch_shape), dtype=np.float32), \
            np.empty((0,), dtype=np.int64)
    return np.stack(sequences, axis=0), np.asarray(seq_labels, dtype=np.int64)


def _finetune_on_labeled(
    model,
    sequences: np.ndarray,
    labels: np.ndarray,
    device,
    epochs_steps: int,
    batch_size: int,
    lr: float,
    frac: float,
) -> None:
    import torch

    if sequences.size == 0 or labels.size == 0 or frac <= 0 or epochs_steps <= 0:
        return
    total = len(labels)
    use_count = max(1, min(int(round(total * frac)), total))
    sequences = sequences[:use_count]
    labels = labels[:use_count]
    dataset = torch.utils.data.TensorDataset(
        torch.from_numpy(sequences),
        torch.from_numpy(labels.astype(np.int64)),
    )
    loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True, drop_last=False)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = torch.nn.CrossEntropyLoss()
    model.train()
    for _ in range(epochs_steps):
        for batch_x, batch_y in loader:
            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)
            optimizer.zero_grad(set_to_none=True)
            logits = model(batch_x)
            loss = criterion(logits, batch_y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
    model.eval()


def _expand_labels(labels: Sequence[int], epoch_seconds: float, output_stride_seconds: float) -> List[int]:
    if output_stride_seconds <= 0:
        raise ValueError("output_stride_seconds must be > 0")
    if abs(epoch_seconds / output_stride_seconds - round(epoch_seconds / output_stride_seconds)) > 1e-6:
        raise ValueError("epoch_seconds must be an integer multiple of output_stride_seconds")
    repeat = int(round(epoch_seconds / output_stride_seconds))
    return [label for label in labels for _ in range(repeat)]


def auto_stage_llm(
    EEG: Sequence[float],
    EMG: Sequence[float],
    label: Optional[Sequence[int]] = None,
    *,
    config: Optional[AutoStageConfig] = None,
) -> List[int]:
    """
    Auto stage a recording using the offline transformer models.

    Parameters
    ----------
    EEG : array-like
        EEG 1-D signal.
    EMG : array-like
        EMG 1-D signal.
    label : list[int] | None
        Optional reference labels used for on-the-fly finetuning. Use 1-3
        for ``stage_id`` mode (NREM/REM/Wake) or 0-2 for ``class`` mode.
        Provide per-second or per-epoch labels depending on
        ``config.label_stride_seconds``.
    config : AutoStageConfig | None
        Configuration for preprocessing, finetuning, and output formatting.

    Returns
    -------
    list of int
        Predicted state codes. Resolution is controlled by
        ``config.output_stride_seconds``.

    Raises
    ------
    ImportError
        When PyTorch is not installed.
    """
    try:
        import torch
    except ImportError as e:  # pragma: no cover
        raise ImportError(
            "The transformer auto-staging requires PyTorch. "
            "Install it with: pip install 'misleep[transformer]' "
            "or pip install torch") from e

    cfg = config or AutoStageConfig()
    model_path = cfg.model_path or default_checkpoint_path()
    if not Path(model_path).exists():
        raise FileNotFoundError(f"Checkpoint not found: {model_path}")

    eeg = _validate_1d(np.asarray(EEG), "EEG")
    emg = _validate_1d(np.asarray(EMG), "EMG")
    if eeg.shape[0] != emg.shape[0]:
        raise ValueError("EEG and EMG must have the same length.")

    device = torch.device(cfg.device or ("cuda" if torch.cuda.is_available() else "cpu"))

    payload = torch.load(model_path, map_location=device, weights_only=False)
    model_cfg: EEGTransformerConfig = payload["config"]
    if cfg.override_model_sample_rate is not None:
        model_cfg.stft.sample_rate = float(cfg.override_model_sample_rate)

    preprocess_cfg = PreprocessConfig(
        sample_rate=cfg.sf,
        epoch_seconds=cfg.epoch_seconds,
        filter_order=cfg.filter_order,
        eeg_band=cfg.eeg_band,
        emg_band=cfg.emg_band,
    )
    context_window = cfg.context_window or model_cfg.context_window

    signal = np.stack([eeg, emg], axis=0)
    sos = build_channel_filters(preprocess_cfg)
    filtered = apply_bandpass(signal, sos)
    standardized = exponential_moving_standardize(filtered, init_window=preprocess_cfg.samples_per_epoch())
    epochs = epoch_signal(standardized, preprocess_cfg)
    if epochs.size == 0:
        return []

    labels_in = label or []
    sample_labels = _labels_to_sample_labels(
        labels_in,
        total_samples=signal.shape[1],
        sf=cfg.sf,
        label_stride_seconds=cfg.label_stride_seconds,
        label_mode=cfg.label_mode,
    )
    epoch_labels = _compute_epoch_labels(sample_labels, preprocess_cfg)
    if epochs.shape[0] != epoch_labels.shape[0]:
        limit = min(epochs.shape[0], epoch_labels.shape[0])
        epochs = epochs[:limit]
        epoch_labels = epoch_labels[:limit]

    sequences, seq_labels = _prepare_sequences(epochs, epoch_labels, context_window)
    model = build_model(cfg.model_name, model_cfg).to(device)
    model.load_state_dict(payload["model_state"])
    model.eval()

    labeled_mask = seq_labels >= 0
    if labeled_mask.any():
        _finetune_on_labeled(
            model,
            sequences[labeled_mask],
            seq_labels[labeled_mask],
            device,
            epochs_steps=cfg.finetune_epochs,
            batch_size=cfg.finetune_batch,
            lr=cfg.finetune_lr,
            frac=cfg.finetune_frac,
        )

    preds: List[int] = []
    loader = torch.utils.data.DataLoader(
        torch.utils.data.TensorDataset(torch.from_numpy(sequences)),
        batch_size=64,
        shuffle=False,
        num_workers=0,
        drop_last=False,
    )
    with torch.no_grad():
        for (batch_x,) in loader:
            batch_x = batch_x.to(device)
            logits = model(batch_x)
            pred = logits.argmax(dim=-1).cpu().numpy()
            preds.extend(pred.tolist())

    if cfg.output_label_mode == "stage_id":
        preds = [p + 1 for p in preds]
    elif cfg.output_label_mode != "class":
        raise ValueError("output_label_mode must be 'stage_id' or 'class'")

    if cfg.output_stride_seconds != cfg.epoch_seconds:
        preds = _expand_labels(preds, cfg.epoch_seconds, cfg.output_stride_seconds)

    return preds
