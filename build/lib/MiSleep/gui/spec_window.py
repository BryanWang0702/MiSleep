# -*- coding: UTF-8 -*-
"""
@Project: MiSleep_v2 
@File: spec_window.py
@Author: Xueqiang Wang
@Date: 2024/3/8
@Description:  
"""

from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtWidgets import QMainWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from misleep.gui.uis.spec_window_ui import Ui_spec_window
import matplotlib.pyplot as plt
from numpy import percentile


class SpecWindow(QMainWindow, Ui_spec_window):
    def __init__(self, parent=None):
        """
        Initialize the spectrum dialog of MiSleep
        """
        super().__init__(parent)

        # Enable high dpi devices
        QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        self.setupUi(self)
        
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

    def show_(self, spectrum, spectrogram, percentile_, ratio):
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
        """

        self.refresh_canvas()

        psd, freq = spectrum
        f, t, Sxx = spectrogram

        # plot 
        self.spectrum_ax.plot(freq, psd)
        self.spectrum_ax.set_ylim(0, max(psd) * 1.1)
        self.spectrum_ax.set_xlim(0, f[-1])
        self.spectrum_ax.set_xlabel("Frequency (Hz)")
        self.spectrum_ax.set_ylabel("Power spectral density (Power/Hz)")

        # Fill the label of delta/theta ratio
        self.DeltaThetaRatioLabel.setText(f"Delta/theta ratio: {ratio}")

        self.spectrogram_ax.set_ylim(0.5, 30)
        cmap = plt.cm.get_cmap('jet')
        pcm = self.spectrogram_ax.pcolormesh(
            t, f, Sxx, cmap=cmap, vmax=percentile(Sxx, percentile_))
        self.spectrogram_figure.colorbar(pcm, ax=self.spectrogram_ax)
        self.spectrogram_ax.set_xlabel("Time (S)")
        self.spectrogram_ax.set_ylabel("Frequency (HZ)")

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

    def spectrogram_save(self):
        """Save spectrogram"""
    

    def closeEvent(self, event):
        event.ignore()
        self.hide()

