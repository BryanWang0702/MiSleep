# -*- coding: UTF-8 -*-
"""Causal-transformer based automatic sleep staging.

This sub-module requires PyTorch (``pip install 'misleep[transformer]'``).
The heavy sub-modules are imported lazily so that importing
``misleep.analysis.transformer`` itself never fails when PyTorch is
missing -- only *using* the auto-staging API does (with a helpful
ImportError).
"""

import importlib
from importlib.resources import files
from pathlib import Path

__all__ = ["AutoStageConfig", "EEGTransformerConfig", "PreprocessConfig",
           "STFTConfig", "auto_stage_llm", "default_checkpoint_path",
           "build_model", "load_mouse_recording", "parse_label_file"]

#: name -> sub-module that provides it
_LAZY_EXPORTS = {
    "AutoStageConfig": "misleep.analysis.transformer.inference",
    "auto_stage_llm": "misleep.analysis.transformer.inference",
    "EEGTransformerConfig": "misleep.analysis.transformer.configs",
    "PreprocessConfig": "misleep.analysis.transformer.configs",
    "STFTConfig": "misleep.analysis.transformer.configs",
    "build_model": "misleep.analysis.transformer.models",
    "load_mouse_recording": "misleep.analysis.transformer.data",
    "parse_label_file": "misleep.analysis.transformer.data",
}


def default_checkpoint_path() -> Path:
    """Return the path of the packaged CausalTransformer checkpoint."""
    ref = files("misleep.analysis.transformer.checkpoints")
    return Path(str(ref)) / "CausalTransformer_best.pt"


def __getattr__(name: str):
    if name in _LAZY_EXPORTS:
        module = importlib.import_module(_LAZY_EXPORTS[name])
        return getattr(module, name)
    raise AttributeError(f"module 'misleep.analysis.transformer' has no attribute {name!r}")


def __dir__():
    return sorted(set(globals()) | set(__all__))
