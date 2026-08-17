# -*- coding: UTF-8 -*-
"""Plotting module (matplotlib, GUI-independent).

These functions are used both by the GUI (embedded in Qt canvases) and by
scripts/Jupyter notebooks to preview signals, spectra and hypnograms.
"""

from .signals import plot_signals
from .spectral import plot_spectrum, plot_spectrogram
from .hypnogram import plot_hypno

__all__ = ["plot_signals", "plot_spectrum", "plot_spectrogram", "plot_hypno"]
