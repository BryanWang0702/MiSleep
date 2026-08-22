# -*- coding: UTF-8 -*-
"""Benchmark auto-staging pipeline for MiSleep (LightGBM + HMM).

Vendored and adapted from the rodent-autostage benchmark models; see
:mod:`misleep.analysis.autostage.benchmark` for the public API used by the
LightGBM auto-staging dialog.
"""

from misleep.analysis.autostage.benchmark import (  # noqa: F401
    EPOCH_S,
    STRIDE,
    W,
    extract_recording,
    load_models,
    model_combo,
    models_path,
    predict_model,
)

__all__ = [
    "EPOCH_S", "STRIDE", "W",
    "extract_recording", "load_models", "model_combo", "models_path",
    "predict_model",
]
