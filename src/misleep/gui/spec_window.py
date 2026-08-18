# -*- coding: UTF-8 -*-
"""Spectrum / spectrogram preview window."""

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox

from misleep.gui.uis.spec_window_ui import Ui_spec_window
from misleep.viz.spectral import spectrogram_color_limits


class SpecWindow(QMainWindow, Ui_spec_window):
    """A standalone window showing the spectrum and spectrogram of a segment."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.start_end = []
        self.spectrum = []
        self.spectrogram = []

        import matplotlib.pyplot as plt

        self.spectrum_figure = plt.figure()
        self.spectrum_ax = self.spectrum_figure.subplots(nrows=1, ncols=1)
        self.spectrum_figure.set_layout_engine("tight")
        self.spectrum_canvas = FigureCanvas(self.spectrum_figure)
        self.SpectrumScrollArea.setWidget(self.spectrum_canvas)
        self.SpectrumSaveBt.clicked.connect(self.spectrum_save)

        self.spectrogram_figure = plt.figure()
        self.spectrogram_ax = self.spectrogram_figure.subplots(nrows=1, ncols=1)
        self.spectrogram_figure.set_layout_engine("tight")
        self.spectrogram_canvas = FigureCanvas(self.spectrogram_figure)
        self.SpectrogramScrollArea.setWidget(self.spectrogram_canvas)
        self.SpectrogramSaveBt.clicked.connect(self.spectrogram_save)
        self.data_path = None

    def show_(self, spectrum, spectrogram, percentile_, ratio, start_end, freq_range, data_path=None):
        """Display a spectrum and spectrogram.

        Parameters
        ----------
        spectrum : list
            ``[psd, freq]`` of the spectrum.
        spectrogram : list
            ``[f, t, Sxx]`` of the spectrogram.
        percentile_ : float
            Percentile used for the spectrogram color scale.
        ratio : float
            Delta/theta ratio (shown in the window).
        start_end : list
            ``[start, end]`` seconds of the analyzed segment.
        freq_range : list
            Frequency range ``[low, high]`` for display.
        data_path : str, optional
            Source data path (used as the default file name when saving).
        """
        self.data_path = data_path
        self.setWindowTitle(f"{start_end[0]} ~ {start_end[1]}")
        self.start_end = start_end
        self.refresh_canvas()

        psd, freq = spectrum
        f, t, Sxx = spectrogram
        self.spectrum = spectrum
        self.spectrogram = spectrogram

        self.spectrum_ax.plot(freq, psd)
        self.spectrum_ax.set_ylim(0, max(psd) * 1.1)
        self.spectrum_ax.set_xlim(freq_range[0], freq_range[1])
        self.spectrum_ax.set_xlabel("Frequency (Hz)")
        self.spectrum_ax.set_ylabel("Power spectral density (Power/Hz)")
        major_ticks_top = np.linspace(0, freq_range[1] + 0.1, 10)
        self.spectrum_ax.xaxis.set_ticks(major_ticks_top)
        self.spectrum_ax.grid(which="major", alpha=0.6)
        self.spectrum_ax.grid(which="minor", alpha=0.3)

        self.DeltaThetaRatioLabel.setText(f"Delta/theta ratio: {ratio}")

        import matplotlib.pyplot as plt

        self.spectrogram_ax.set_ylim(freq_range[0], freq_range[1] + 0.1)
        from misleep.config import load_config

        cmap_name = load_config().get("gui", "spectrogram_cmap", fallback="jet")
        try:
            cmap = plt.get_cmap(cmap_name)
        except ValueError:
            cmap = plt.get_cmap("jet")
        vmin, vmax = spectrogram_color_limits(Sxx, percentile_)
        self.spectrogram_ax.set_facecolor(cmap(0.0))
        pcm = self.spectrogram_ax.pcolormesh(
            t, f, Sxx, cmap=cmap, vmin=vmin, vmax=vmax, shading="auto")
        self.spectrogram_figure.colorbar(pcm, ax=self.spectrogram_ax)
        self.spectrogram_ax.set_xlabel("Time (s)")
        self.spectrogram_ax.set_ylabel("Frequency (Hz)")

        self.spectrum_figure.canvas.draw()
        self.spectrum_figure.canvas.flush_events()
        self.spectrogram_figure.canvas.draw()
        self.spectrogram_figure.canvas.flush_events()

    def refresh_canvas(self):
        import matplotlib.pyplot as plt

        plt.close(self.spectrum_figure)
        plt.close(self.spectrogram_figure)

        self.spectrum_figure = plt.figure()
        self.spectrum_ax = self.spectrum_figure.subplots(nrows=1, ncols=1)
        self.spectrum_figure.set_layout_engine("tight")
        self.spectrum_canvas = FigureCanvas(self.spectrum_figure)
        self.SpectrumScrollArea.setWidget(self.spectrum_canvas)

        self.spectrogram_figure = plt.figure()
        self.spectrogram_ax = self.spectrogram_figure.subplots(nrows=1, ncols=1)
        self.spectrogram_figure.set_layout_engine("tight")
        self.spectrogram_canvas = FigureCanvas(self.spectrogram_figure)
        self.SpectrogramScrollArea.setWidget(self.spectrogram_canvas)

    def spectrum_save(self):
        import pandas as pd

        fd, _ = QFileDialog.getSaveFileName(
            self, "Save figure and data",
            f"{self.data_path}_spectrum_{self.start_end[0]}_{self.start_end[1]}",
            "*.pdf;;*.png;;*.tif;;*.eps;;")
        if fd == "":
            return

        self.setDisabled(True)
        self.spectrum_figure.savefig(fd, dpi=300)
        data_path = fd[:-4]
        fd = data_path + "_data.csv"
        try:
            _df = pd.DataFrame(
                data=np.array([[f"{value:.2f}" for value in self.spectrum[1]], self.spectrum[0]]).T,
                columns=["frequency", "power"])
            _df.to_csv(fd, index=False)
        except PermissionError:
            QMessageBox.about(
                self, "Error",
                "Permission error, please check if the file is open in other programs.")
        self.setEnabled(True)

    def spectrogram_save(self):
        import pandas as pd

        fd, _ = QFileDialog.getSaveFileName(
            self, "Save figure and data",
            f"{self.data_path}_spectrogram_{self.start_end[0]}_{self.start_end[1]}",
            "*.pdf;;*.tif;;*.png;;*.eps;;")
        if fd == "":
            return

        self.setDisabled(True)
        self.spectrogram_figure.savefig(fd, dpi=300)

        data_path = fd[:-4]
        fd = data_path + "_data.csv"
        try:
            _df = pd.DataFrame(
                self.spectrogram[2].T,
                index=[f"{value:.2f}" for value in self.spectrogram[1]],
                columns=[f"{value:.2f}" for value in self.spectrogram[0]])
            _df.to_csv(fd, index=True)
        except PermissionError:
            QMessageBox.about(
                self, "Error",
                "Permission error, please check if the file is open in other programs.")
        self.setEnabled(True)

    def closeEvent(self, event):
        """Release matplotlib figures; they are recreated on the next show."""
        import matplotlib.pyplot as plt

        plt.close(self.spectrum_figure)
        plt.close(self.spectrogram_figure)
        event.ignore()
        self.hide()
