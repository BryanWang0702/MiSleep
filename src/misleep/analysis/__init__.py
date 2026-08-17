# -*- coding: UTF-8 -*-
"""Analysis module: event detection and automatic sleep staging.

* :mod:`misleep.analysis.detection`     -- SWA / spindle / artifact detection
* :mod:`misleep.analysis.features`      -- auto-staging feature extraction
* :mod:`misleep.analysis.auto_stage`    -- LightGBM auto staging
* :mod:`misleep.analysis.transformer`   -- Causal-transformer auto staging (PyTorch)

The transformer sub-module is only imported on demand because it requires
PyTorch, which is not available on every platform.
"""

from .detection import SWA_detection, spindle_detection, artifact_detection
from .auto_stage import auto_stage_gbm, result_constraints, model_path

__all__ = [
    "SWA_detection",
    "spindle_detection",
    "artifact_detection",
    "auto_stage_gbm",
    "result_constraints",
    "model_path",
]
