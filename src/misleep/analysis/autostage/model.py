# -*- coding: UTF-8 -*-
"""LightGBM classifier inference for the benchmark auto-staging models."""

from __future__ import annotations

import numpy as np


def _import_lightgbm():
    try:
        import lightgbm as lgb
        return lgb
    except ImportError as e:  # pragma: no cover
        raise ImportError(
            "Auto staging requires 'lightgbm'. Install it with "
            "`pip install lightgbm` or `pip install 'misleep[analysis]'`."
        ) from e


def predict_lgbm(model_dict, X):
    """Return predicted probabilities (n, n_classes) from a model dict."""
    _import_lightgbm()
    model = model_dict["model"]
    it = model_dict.get("best_iteration", None)
    if it is not None and it > 0:
        return model.predict_proba(X, num_iteration=it)
    return model.predict_proba(X)
