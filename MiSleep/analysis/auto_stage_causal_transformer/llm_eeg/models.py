from __future__ import annotations

import math
from typing import Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

from .configs import EEGTransformerConfig, STFTConfig


class ConvFeatureExtractor(nn.Module):
    def __init__(self, in_channels: int, base_filters: int, kernel_size: int, conv_blocks: int, embed_dim: int) -> None:
        super().__init__()
        padding = kernel_size // 2
        layers = []
        current_channels = in_channels
        filters = base_filters
        for _ in range(conv_blocks):
            layers.append(nn.Conv1d(current_channels, filters, kernel_size, padding=padding))
            layers.append(nn.BatchNorm1d(filters))
            layers.append(nn.ReLU(inplace=True))
            current_channels = filters
            filters *= 2
        self.conv = nn.Sequential(*layers)
        self.pool = nn.AdaptiveAvgPool1d(1)
        self.proj = nn.Linear(current_channels, embed_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        features = self.conv(x)
        pooled = self.pool(features).squeeze(-1)
        return F.relu(self.proj(pooled))


def infer_stft_feature_dim(cfg: STFTConfig) -> int:
    nyquist = cfg.sample_rate / 2.0
    max_freq = min(cfg.f_max, nyquist)
    freq_resolution = cfg.sample_rate / cfg.n_fft
    max_bin = max(int(math.floor(max_freq / max(freq_resolution, 1e-6))), 0)
    return min(cfg.n_fft // 2 + 1, max_bin + 1)


def compute_stft_features(x: torch.Tensor, cfg: STFTConfig) -> torch.Tensor:
    bsz, window, channels, samples = x.shape
    if channels == 0:
        raise ValueError("Input tensor must contain at least one channel for STFT features.")
    device = x.device
    window_fn = torch.hann_window(cfg.win_length, device=device)
    eeg = x[:, :, 0, :]  # use EEG_P for spectral features
    flat = eeg.reshape(bsz * window, samples)
    spec = torch.stft(
        flat,
        n_fft=cfg.n_fft,
        hop_length=cfg.hop_length,
        win_length=cfg.win_length,
        window=window_fn,
        return_complex=True,
        onesided=True,
        normalized=False,
    )
    freqs = torch.fft.rfftfreq(cfg.n_fft, d=1.0 / cfg.sample_rate).to(device)
    mask = freqs <= cfg.f_max
    spec = spec[:, mask, :]
    mag = torch.log1p(spec.abs())
    mag = mag.mean(dim=-1)  # (B*W, F_keep)
    return mag.view(bsz, window, -1)


class ConvEpochEncoder(nn.Module):
    def __init__(self, in_channels: int, hidden_dim: int) -> None:
        super().__init__()
        layers = []
        current = in_channels
        for out in (hidden_dim // 2, hidden_dim):
            layers.append(nn.Conv1d(current, out, kernel_size=7, padding=3, stride=2))
            layers.append(nn.BatchNorm1d(out))
            layers.append(nn.GELU())
            current = out
        layers.append(nn.AdaptiveAvgPool1d(1))
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        bsz, window, channels, samples = x.shape
        out = self.net(x.view(bsz * window, channels, samples)).squeeze(-1)
        return out.view(bsz, window, -1)


class FeedForward(nn.Module):
    def __init__(self, dim: int, hidden: int, dropout: float) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(dim, hidden),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden, dim),
            nn.Dropout(dropout),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class CausalBlock(nn.Module):
    def __init__(self, dim: int, heads: int, dropout: float) -> None:
        super().__init__()
        self.attn = nn.MultiheadAttention(dim, heads, dropout=dropout, batch_first=True)
        self.ln1 = nn.LayerNorm(dim)
        self.ln2 = nn.LayerNorm(dim)
        self.ff = FeedForward(dim, dim * 4, dropout)

    def forward(self, x: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        attn_out, _ = self.attn(self.ln1(x), self.ln1(x), self.ln1(x), attn_mask=mask)
        x = x + attn_out
        x = x + self.ff(self.ln2(x))
        return x


class CausalTransformerClassifier(nn.Module):
    def __init__(self, cfg: EEGTransformerConfig) -> None:
        super().__init__()
        self.cfg = cfg
        self.context_window = max(1, cfg.context_window)
        self.local_encoder = ConvEpochEncoder(2, cfg.d_model)
        spec_dim = infer_stft_feature_dim(cfg.stft)
        self.spec_linear = nn.Sequential(
            nn.Linear(spec_dim, cfg.d_model),
            nn.GELU(),
            nn.LayerNorm(cfg.d_model),
        )
        self.fuse = nn.Sequential(
            nn.Linear(cfg.d_model * 2, cfg.d_model),
            nn.GELU(),
        )
        self.pos_embed = nn.Parameter(torch.randn(1, self.context_window, cfg.d_model) / math.sqrt(cfg.d_model))
        self.blocks = nn.ModuleList(
            [CausalBlock(cfg.d_model, cfg.num_heads, cfg.dropout) for _ in range(cfg.num_layers)]
        )
        self.norm = nn.LayerNorm(cfg.d_model)
        self.head = nn.Linear(cfg.d_model, cfg.num_classes)

    def forward(self, x: torch.Tensor, return_features: bool = False, ablate_spec: bool = False):
        if x.dim() == 3:
            x = x.unsqueeze(1)
        bsz, window, channels, samples = x.shape
        assert window == self.context_window, f"Expected {self.context_window} epochs, got {window}"
        local = self.local_encoder(x)
        spec = compute_stft_features(x, self.cfg.stft)
        if ablate_spec:
            spec = torch.zeros_like(spec)
        if spec.size(-1) != self.spec_linear[0].in_features:
            target = self.spec_linear[0].in_features
            if spec.size(-1) > target:
                spec = spec[..., :target]
            else:
                spec = F.pad(spec, (0, target - spec.size(-1)))
        spec = self.spec_linear(spec)
        tokens = self.fuse(torch.cat([local, spec], dim=-1)) + self.pos_embed
        mask = torch.triu(torch.ones(window, window, device=x.device), diagonal=1).bool()
        for block in self.blocks:
            tokens = block(tokens, mask)
        features = self.norm(tokens[:, -1, :])
        logits = self.head(features)
        if return_features:
            return logits, features
        return logits


class ConvTransformerClassifier(nn.Module):
    def __init__(self, cfg: EEGTransformerConfig) -> None:
        super().__init__()
        self.cfg = cfg
        self.context_window = max(1, cfg.context_window)
        self.feature_extractor = ConvFeatureExtractor(
            in_channels=2,
            base_filters=cfg.conv_base_filters,
            kernel_size=cfg.conv_kernel_size,
            conv_blocks=cfg.conv_blocks,
            embed_dim=cfg.d_model,
        )
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=cfg.d_model,
            nhead=cfg.num_heads,
            dim_feedforward=cfg.dim_feedforward,
            dropout=cfg.dropout,
            batch_first=True,
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=cfg.num_layers)
        self.pos_embed = nn.Parameter(torch.zeros(1, self.context_window, cfg.d_model))
        self.norm = nn.LayerNorm(cfg.d_model)
        self.head = nn.Sequential(
            nn.Linear(cfg.d_model, cfg.dim_feedforward),
            nn.ReLU(inplace=True),
            nn.Dropout(cfg.dropout),
            nn.Linear(cfg.dim_feedforward, cfg.num_classes),
        )

    def forward(self, x: torch.Tensor, return_features: bool = False):
        if x.dim() == 3:
            x = x.unsqueeze(1)
        bsz, window, channels, samples = x.shape
        assert window == self.context_window, f"Expected {self.context_window} epochs, got {window}"
        feats = self.feature_extractor(x.view(bsz * window, channels, samples)).view(bsz, window, -1)
        tokens = feats + self.pos_embed[:, :window, :]
        encoded = self.transformer(tokens)
        pooled = self.norm(encoded.mean(dim=1))
        logits = self.head(pooled)
        if return_features:
            return logits, pooled
        return logits


def build_model(name: str, config: EEGTransformerConfig) -> nn.Module:
    if name == "CausalTransformer":
        return CausalTransformerClassifier(config)
    if name == "ConvTransformer":
        return ConvTransformerClassifier(config)
    raise ValueError("Unknown model. Choices: CausalTransformer, ConvTransformer.")
