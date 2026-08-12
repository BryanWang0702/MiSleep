from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass()
class PreprocessConfig:
    """signal preprocessing hyperparameters"""

    sample_rate: float = 305.1758
    epoch_seconds: float = 5.0
    filter_order: int = 4
    eeg_band: Tuple[float, float] = (0.5, 30.0)
    emg_band: Tuple[float, float] = (15.0, 100.0)

    def samples_per_epoch(self) -> int:
        return int(round(self.sample_rate * self.epoch_seconds))

    def hop_length_samples(self) -> int:
        return self.samples_per_epoch()


@dataclass()
class STFTConfig:
    """STFT hyperparameters"""

    sample_rate: float = 305.1758
    n_fft: int = 256
    hop_length: int = 128
    win_length: int = 256
    f_max: float = 40.0


@dataclass()
class EEGTransformerConfig:
    """Light-Transformer"""

    num_classes: int = 3
    patch_size: int = 32
    d_model: int = 128
    num_heads: int = 4
    num_layers: int = 4
    dim_feedforward: int = 256
    dropout: float = 0.1
    use_time_tokens: bool = True
    use_spec_tokens: bool = True
    stft: STFTConfig = field(default_factory=STFTConfig)
    context_window: int = 11
    conv_base_filters: int = 16
    conv_kernel_size: int = 7
    conv_blocks: int = 2
