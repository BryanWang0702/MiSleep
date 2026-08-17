# -*- coding: UTF-8 -*-
"""Input/output module.

Public API:

* :func:`misleep.io.mat.load_mat` / :func:`misleep.io.mat.write_mat`
* :func:`misleep.io.edf.load_edf` / :func:`misleep.io.edf.write_edf`
* :func:`misleep.io.annotation.load_misleep_anno` / ``save_misleep_anno``
* :func:`misleep.io.annotation.transfer_result`
* :func:`misleep.io.base.load_signal` / ``write_signal`` -- extension dispatch
"""

from .base import (
    MiData,
    MiAnnotation,
    register_signal_reader,
    register_signal_writer,
    load_signal,
    write_signal,
    available_readers,
    available_writers,
)
from .mat import load_mat, write_mat
from .edf import load_edf, write_edf
from .annotation import load_misleep_anno, save_misleep_anno, load_bio_anno, transfer_result

# Register built-in formats
from . import mat as _mat  # noqa: F401  (triggers register_signal_*)
from . import edf as _edf  # noqa: F401

__all__ = [
    "MiData",
    "MiAnnotation",
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
    "register_signal_reader",
    "register_signal_writer",
    "available_readers",
    "available_writers",
]
