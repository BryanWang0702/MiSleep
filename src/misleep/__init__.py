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

from misleep.data import MiData, MiAnnotation
from misleep.io import (
    load_mat,
    write_mat,
    load_edf,
    write_edf,
    load_misleep_anno,
    save_misleep_anno,
    load_bio_anno,
    transfer_result,
    load_signal,
    write_signal,
)
from misleep.preprocessing import (
    signal_filter,
    filter_power_line_noise,
    z_score,
    reject_artifact,
    spectrum,
    spectrogram,
    band_power,
    crop_state_data,
)
from misleep.analysis import (
    SWA_detection,
    spindle_detection,
    artifact_detection,
    auto_stage_gbm,
    result_constraints,
)
from misleep.viz import plot_signals, plot_spectrum, plot_spectrogram, plot_hypno
from misleep import utils  # noqa: F401  (expose misleep.utils namespace)

__author__ = "Xueqiang Wang <swang9194@gmail.com>"
__version__ = "0.3.0"

__all__ = [
    # data
    "MiData",
    "MiAnnotation",
    # io
    "load_mat",
    "write_mat",
    "load_edf",
    "write_edf",
    "load_misleep_anno",
    "save_misleep_anno",
    "load_bio_anno",
    "transfer_result",
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
