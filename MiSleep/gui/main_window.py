# -*- coding: UTF-8 -*-
"""
@Project: MiSleep_v2
@File: main_window.py
@Author: Xueqiang Wang
@Date: 2024/3/8
@Description:  Main window of MiSleep gui
"""
from datetime import datetime

from PyQt5.QtCore import QCoreApplication, Qt, QStringListModel
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QAction

from misleep import spectrogram
from misleep.viz.spectral import plot_spectrogram
from misleep.viz.signals import plot_signals
from misleep.io.base import MiData, MiAnnotation
from misleep.io.signal_io import load_mat, load_edf
from misleep.io.annotation_io import load_misleep_anno
from misleep.utils.annotation import create_new_mianno
from misleep.gui.about import about_dialog
from misleep.gui.uis import Ui_MiSleep


class main_window(QMainWindow, Ui_MiSleep):
    def __init__(self, parent=None):
        """
        Initialize the Main Window of MiSleep, load data in the toolBar area
        """
        super().__init__(parent)

        # Enable high dpi devices
        QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        self.setupUi(self)

        self.midata = None
        self.mianno = None

        # original data and label file path
        self.data_path = ""
        self.anno_path = ""

        # Set initial params
        self.current_sec = 0
        self.current_y_lims = None  # list of y lim for each channel
        self.current_y_shift = None  # list of y shift for each channel
        self.show_idx = None  # Channels to show in plot area
        self.state_map_dict = {1: 'NREM', 2: 'REM', 3: 'Wake', 4: 'INIT'}
        self.current_spectrogram_idx = 0
        self.spectrogram_percentile = 99.7

        # Initial params for widgets
        self.channel_slm = QStringListModel()

        # Initial about dialog and spec window
        self.about_dialog = about_dialog()

        self.init_qt()

    def init_qt(self):
        """Initial actions for qt widgets"""
        # Set triggers for toolBars
        self.AboutBar.actionTriggered[QAction].connect(self.about_bar_dispatcher)
        self.LoadBar.actionTriggered[QAction].connect(self.load_bar_dispatcher)
        self.SaveBar.actionTriggered[QAction].connect(self.save_bar_dispatcher)

        # Set original time
        self.AcTimeEdit.setDateTime(datetime.now())

        self.PercentileSpin.setValue(self.spectrogram_percentile)

    def load_data(self):
        """Triggered by actionLoad_Data, get MiData"""
        data_path, _ = QFileDialog.getOpenFileName(self, 'Select data file', r'',
                                                   'Matlab Files (*.mat *.MAT);;EDF Files (*.edf *.EDF)')

        if data_path == "":
            return
        self.data_path = data_path
        if self.data_path.endswith(('.mat', '.MAT')):
            try:
                self.midata = load_mat(data_path=self.data_path)
            except Exception:
                QMessageBox.about(self, "Error",
                                  r"Data file invalid, check "
                                  r"<a href='https://github.com/BryanWang0702/MiSleep'>MiSleep</a> for detail.")
                self.data_path = ""
                return

        if self.data_path.endswith(('.edf', '.EDF')):
            try:
                self.midata = load_edf(data_path=self.data_path)
            except Exception:
                QMessageBox.about(self, "Error",
                                  r"Data file invalid, check "
                                  r"<a href='https://github.com/BryanWang0702/MiSleep'>MiSleep</a> for detail.")
                self.data_path = ""
                return

        # Set meta info
        self.DataPathEdit.setText(self.data_path)
        self.AcTimeEdit.setDateTime(datetime.strptime(self.midata.time, "%Y%m%d-%H:%M:%S"))

        # Set channel infos
        self.fill_channel_listView()

    def load_anno(self):
        """Triggered by actionLoad_Annotation"""
        anno_path, _ = QFileDialog.getOpenFileName(self, 'Select annotation file', r'',
                                                   'txt Files (*.txt *.TXT)')

        if anno_path == "":
            return
        self.anno_path = anno_path

        if self.anno_path.endswith(('.txt', '.TXT')):
            try:
                self.mianno = load_misleep_anno(self.anno_path)
            except AssertionError as e:
                if e == "Empty":
                    if isinstance(self.midata, MiData):
                        self.mianno = create_new_mianno(self.midata.duration)
                    else:
                        QMessageBox.about(self, "Error",
                                          "To create a new annotation file, load a data file first.")
                        self.anno_path = ""
                        return

                if e == "Invalid":
                    QMessageBox.about(self, "Error",
                                      r"Annotation file invalid, check "
                                      r"<a href='https://github.com/BryanWang0702/MiSleep'>MiSleep</a> for detail.")
                    self.data_path = ""
                    return
        # Set meta info
        self.AnnoPathEdit.setText(self.anno_path)

    def check_show(self):
        """Check and show all, triggered by actionShow"""
        if not isinstance(self.midata, MiData) or not isinstance(self.mianno, MiAnnotation):
            QMessageBox.about(self, "Error",
                              r"Load data file and annotation file first.")
            return

        if self.midata.duration != self.mianno.anno_length:
            QMessageBox.about(self, "Error",
                              r"Seems that annotation length is different with data duration.")
            return

        self.plot_signals()
        self.plot_hypo()

    def plot_signals(self):
        """Main plot function, plot signal area, including the spectrogram"""
        f, t, Sxx = spectrogram(signal=self.midata.signals[self.current_spectrogram_idx],
                                sf=self.midata.sf[self.current_spectrogram_idx],
                                step=1, window=5, norm=True)
        fig_spec, ax_spec = plot_spectrogram(f, t, Sxx, percentile=self.spectrogram_percentile)
        fig_signal, axs_signal = plot_signals(signals=self.midata.signals,
                                              ch_names=self.midata.channels,
                                              sf=self.midata.sf)
        fig_signal

    def plot_hypo(self):
        """Plot hypnogram area"""

    def fill_channel_listView(self):
        """Fill channel listView with self.midata.channels"""
        self.channel_slm.setStringList(self.midata.channels)
        self.ChListView.setModel(self.channel_slm)

    def about_bar_dispatcher(self, signal):
        """Triggered by AboutBar action, show About dialog"""
        if signal.text() == 'About':
            self.about_dialog.exec()

    def load_bar_dispatcher(self, signal):
        """Triggered by LoadBar action, load data, load annotation, show"""
        if signal.text() == 'Load Data':
            self.load_data()
        if signal.text() == 'Load Annotation':
            self.load_anno()
        if signal.text() == 'Show':
            self.check_show()

    def save_bar_dispatcher(self, signal):
        """Triggered by SaveBar action, save data, save annotation"""
        pass
