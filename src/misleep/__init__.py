# -*- coding: UTF-8 -*-
"""MiSleep: mice sleep EEG/EMG visualization, scoring, and analysis.

MiSleep is organized into a small number of modules:

=================  ======================================================
Module             Purpose
=================  ======================================================
``misleep.data``   in-memory data containers (MiData, MiAnnotation)
``misleep.io``     load/save signals (``.mat``, ``.edf``) and annotations
``misleep.preprocessing`` filtering, artifact rejection, spectral analysis
``misleep.analysis`` event detection and automatic sleep staging
``misleep.viz``    matplotlib plotting (signals, spectra, hypnograms)
``misleep.gui``    PySide6 desktop application (``python -m misleep``)
``misleep.utils``  small helpers
=================  ======================================================

The GUI is intentionally *not* imported here so that the core package
works without PySide6; import ``misleep.gui`` explicitly when needed.
"""

from importlib import import_module

__author__ = "Xueqiang Wang <swang9194@gmail.com>"
__version__ = "0.3.1"

# Importing ``misleep`` used to import scipy, pandas, sklearn and matplotlib
# immediately.  The GUI necessarily imports some of those later, but making
# the public convenience API lazy removes a large block of duplicate startup
# work and keeps lightweight uses such as ``misleep.__version__`` instant.
_LAZY_EXPORTS = {
    "MiData": ("misleep.data", "MiData"),
    "MiAnnotation": ("misleep.data", "MiAnnotation"),
    **{name: ("misleep.io", name) for name in (
        "load_mat", "write_mat", "load_edf", "write_edf", "load_npy",
        "load_npz", "load_csv", "load_tsv", "write_npz",
        "load_misleep_anno", "save_misleep_anno", "load_bio_anno",
        "transfer_result", "load_annotation", "load_json_anno",
        "load_table_anno", "load_signal", "write_signal")},
    **{name: ("misleep.preprocessing", name) for name in (
        "signal_filter", "filter_power_line_noise", "z_score",
        "reject_artifact", "spectrum", "spectrogram", "band_power",
        "crop_state_data")},
    **{name: ("misleep.analysis", name) for name in (
        "SWA_detection", "spindle_detection", "artifact_detection",
        "auto_stage_gbm", "result_constraints")},
    **{name: ("misleep.viz", name) for name in (
        "plot_signals", "plot_spectrum", "plot_spectrogram", "plot_hypno")},
    "utils": ("misleep.utils", None),
}


def __getattr__(name):
    """Load public convenience exports only when first accessed."""
    try:
        module_name, attribute = _LAZY_EXPORTS[name]
    except KeyError as exc:
        raise AttributeError(f"module 'misleep' has no attribute {name!r}") from exc
    module = import_module(module_name)
    value = module if attribute is None else getattr(module, attribute)
    globals()[name] = value
    return value


def __dir__():
    return sorted(set(globals()) | set(_LAZY_EXPORTS))

__all__ = [
    # data
    "MiData",
    "MiAnnotation",
    # io
    "load_mat",
    "write_mat",
    "load_edf",
    "write_edf",
    "load_npy",
    "load_npz",
    "load_csv",
    "load_tsv",
    "write_npz",
    "load_misleep_anno",
    "save_misleep_anno",
    "load_bio_anno",
    "transfer_result",
    "load_annotation",
    "load_json_anno",
    "load_table_anno",
    "load_signal",
    "write_signal",
    # preprocessing
    "signal_filter",
    "filter_power_line_noise",
    "z_score",
    "reject_artifact",
    "spectrum",
    "spectrogram",
    "band_power",
    "crop_state_data",
    # analysis
    "SWA_detection",
    "spindle_detection",
    "artifact_detection",
    "auto_stage_gbm",
    "result_constraints",
    # viz
    "plot_signals",
    "plot_spectrum",
    "plot_spectrogram",
    "plot_hypno",
]
