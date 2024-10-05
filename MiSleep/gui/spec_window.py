# -*- coding: UTF-8 -*-
"""
@Project: MiSleep_v2 
@File: spec_window.py
@Author: Xueqiang Wang
@Date: 2024/3/8
@Description:  
"""

from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtWidgets import QMainWindow, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from misleep.gui.uis.spec_window_ui import Ui_spec_window
import matplotlib.pyplot as plt
import numpy as np


class SpecWindow(QMainWindow, Ui_spec_window):
    def __init__(self, parent=None):
        """
        Initialize the spectrum dialog of MiSleep
        """
        super().__init__(parent)

        self.setupUi(self)

        self.start_end = []
        self.spectrum = []
        self.spectrogram = []

        # initialize the figures for spectrum, and spectrogram
        self.spectrum_figure = plt.figure()
        self.spectrum_ax = self.spectrum_figure.subplots(nrows=1, ncols=1)

        self.spectrum_figure.set_tight_layout(True)
        self.spectrum_canvas = FigureCanvas(self.spectrum_figure)
        self.SpectrumScrollArea.setWidget(self.spectrum_canvas)
        self.SpectrumSaveBt.clicked.connect(self.spectrum_save)

        self.spectrogram_figure = plt.figure()
        self.spectrogram_ax = self.spectrogram_figure.subplots(nrows=1, ncols=1)
        self.spectrogram_figure.set_tight_layout(True)
        self.spectrogram_canvas = FigureCanvas(self.spectrogram_figure)
        self.SpectrogramScrollArea.setWidget(self.spectrogram_canvas)
        self.SpectrogramSaveBt.clicked.connect(self.spectrogram_save)

    def show_(self, spectrum, spectrogram, percentile_, ratio, start_end):
        """Pass in the spectrum and spectrogram
        Parameters
        ----------
        spectrum : list
            [psd, spec] of spectrum
        spectrogram :  list
            [f, t, Sxx] of spectrogram
        percentile : float
            Percentile of color in spectrogram
        ratio : float
            Ratio of delta/theta
        start_end : list
            Start end for the spectral analysis, will be used for
            the window title and save params
        """

        self.setWindowTitle(f"{start_end[0]} ~ {start_end[1]}")
        self.start_end = start_end
        self.refresh_canvas()

        psd, freq = spectrum
        f, t, Sxx = spectrogram
        self.spectrum = spectrum
        self.spectrogram = spectrogram

        # plot
        self.spectrum_ax.plot(freq, psd)
        self.spectrum_ax.set_ylim(0, max(psd) * 1.1)
        self.spectrum_ax.set_xlim(0, 30)
        self.spectrum_ax.set_xlabel("Frequency (Hz)")
        self.spectrum_ax.set_ylabel("Power spectral density (Power/Hz)")
        major_ticks_top = np.linspace(0, 30, 16)
        minor_ticks_top = np.linspace(0, 30, 31)

        self.spectrum_ax.xaxis.set_ticks(major_ticks_top)
        self.spectrum_ax.xaxis.set_ticks(minor_ticks_top, minor=True)
        self.spectrum_ax.grid(which="major", alpha=0.6)
        self.spectrum_ax.grid(which="minor", alpha=0.3)

        # Fill the label of delta/theta ratio
        self.DeltaThetaRatioLabel.setText(f"Delta/theta ratio: {ratio}")

        self.spectrogram_ax.set_ylim(0.5, 30)
        cmap = plt.cm.get_cmap("jet")
        pcm = self.spectrogram_ax.pcolormesh(
            t, f, Sxx, cmap=cmap, vmax=np.percentile(Sxx, percentile_)
        )
        self.spectrogram_figure.colorbar(pcm, ax=self.spectrogram_ax)
        self.spectrogram_ax.set_xlabel("Time (s)")
        self.spectrogram_ax.set_ylabel("Frequency (Hz)")

        self.spectrum_figure.canvas.draw()
        self.spectrum_figure.canvas.flush_events()
        self.spectrogram_figure.canvas.draw()
        self.spectrogram_figure.canvas.flush_events()

    def refresh_canvas(self):
        """Refresh all the figures"""
        self.spectrum_figure = plt.figure()
        self.spectrum_ax = self.spectrum_figure.subplots(nrows=1, ncols=1)
        self.spectrum_figure.set_tight_layout(True)
        self.spectrum_canvas = FigureCanvas(self.spectrum_figure)
        self.SpectrumScrollArea.setWidget(self.spectrum_canvas)

        self.spectrogram_figure = plt.figure()
        self.spectrogram_ax = self.spectrogram_figure.subplots(nrows=1, ncols=1)

        self.spectrogram_figure.set_tight_layout(True)
        self.spectrogram_canvas = FigureCanvas(self.spectrogram_figure)
        self.SpectrogramScrollArea.setWidget(self.spectrogram_canvas)

    def spectrum_save(self):
        """Save spectrum"""
        fd, _ = QFileDialog.getSaveFileName(
            self,
            "Save figure and data",
            f"spectrum_{self.start_end[0]}_{self.start_end[1]}",
            "*.pdf;;*.png;;*.tif;;*.eps;;",
        )
        if fd == "":
            return

        self.setDisabled(True)
        self.spectrum_figure.savefig(fd, dpi=300)
        data_path = fd[:-4]
        fd = data_path + "_data.csv"

        data_arr = np.array([self.spectrum[1], self.spectrum[0]]).transpose()
        np.savetxt(fd, X=data_arr, delimiter=",")

        self.setEnabled(True)

    def spectrogram_save(self):
        """Save spectrogram"""

        fd, _ = QFileDialog.getSaveFileName(
            self,
            "Save figure and data",
            f"spectrogram_{self.start_end[0]}_{self.start_end[1]}",
            "*.pdf;;*.tif;;*.png;;*.eps;;",
        )
        if fd == "":
            return

        self.setDisabled(True)
        self.spectrogram_figure.savefig(fd, dpi=300)
        self.setEnabled(True)

    def closeEvent(self, event):
        event.ignore()
        self.hide()
