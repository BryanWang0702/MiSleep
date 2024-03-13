# -*- coding: UTF-8 -*-
"""
@Project: MiSleep_v2
@File: main_window.py
@Author: Xueqiang Wang
@Date: 2024/3/8
@Description:  Main window of MiSleep gui
"""
import copy
import datetime

import numpy as np
from PyQt5.QtCore import QCoreApplication, Qt, QStringListModel
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QAction
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from misleep.preprocessing.spectral import spectrogram
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
        self.show_duration = 30  # Seconds of duration to plot
        self.y_lims = None  # list of y lim for each channel
        self.y_shift = None  # list of y shift for each channel
        self.show_idx = None  # Channels to show in plot area
        self.state_map_dict = {1: 'NREM', 2: 'REM', 3: 'Wake', 4: 'INIT'}
        self.ShowRangeCombo_dict = {0: 30, 1: 60, 2: 300, 3: 1800, 4: 3600}
        self.current_spectrogram_idx = 0
        self.spectrogram_percentile = 99.7
        self.show_midata = None
        self.epoch_length = 5
        self.ac_time = None

        # Signal area figure
        self.signal_figure = plt.figure()
        self.signal_ax = self.signal_figure.subplots()
        self.signal_figure.set_tight_layout(True)
        self.signal_figure.tight_layout(h_pad=0, w_pad=0)
        self.signal_figure.subplots_adjust(hspace=0)  # Adjust subplots
        self.signal_canvas = FigureCanvas(self.signal_figure)
        # Add button click release event for signal canvas
        self.signal_canvas.mpl_connect("button_release_event", self.click_signal)

        # Hypnogram area figure
        self.hypo_figure = plt.figure(layout='constrained')
        self.hypo_ax = self.hypo_figure.subplots()
        self.hypo_canvas = FigureCanvas(self.hypo_figure)
        self.hypo_canvas.mpl_connect("button_release_event", self.click_hypo)
        # self.hypo_axvline = self.hypo_ax.axvline(self.current_sec, color='gray', alpha=0.8)

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

        # Spectrogram percentile change
        self.PercentileSpin.setValue(self.spectrogram_percentile)
        self.PercentileSpin.setRange(0, 100)
        self.PercentileSpin.valueChanged.connect(self.spec_percentile_change)
        # Spectrogram default channel
        self.DefaultCh4SpecBt.clicked.connect(self.default_ch4Spec)

        # Scroll bar
        self.ScrollerBar.valueChanged.connect(self.scroller_change)
        self.ScrollerBar.setSingleStep(self.epoch_length)
        self.ScrollerBar.setPageStep(self.show_duration)

        # Time edit
        self.SecondSpin.valueChanged.connect(self.SecondSpin_change)
        self.DateTimeEdit.dateTimeChanged.connect(self.DateTimeEdit_change)

        # Channel operations
        self.ShowChBt.clicked.connect(self.show_chs)
        self.HideChBt.clicked.connect(self.hide_chs)
        self.DeleteChBt.clicked.connect(self.delete_chs)
        self.ScalerUpBt.clicked.connect(self.scaler_up)
        self.ScalerDownBt.clicked.connect(self.scaler_down)
        self.ShiftUpBt.clicked.connect(self.shift_up)
        self.ShiftDownBt.clicked.connect(self.shift_down)

        # Custom second spin edit and ShowRangeCombo
        self.ShowRangeCombo.setEnabled(True)
        self.EpochNumSpin.setDisabled(True)
        self.EpochNumSpin.setRange(1, 720)
        self.EpochNumSpin.setValue(6)
        self.EpochNumSpin.valueChanged.connect(self.EpochNumSpin_changed)
        self.ShowRangeCombo.currentIndexChanged.connect(self.ShowRangeCombo_changed)
        self.CustomSecondsCheck.clicked.connect(self.CustomSecondCheck_clicked)

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
        self.ac_time = datetime.datetime.strptime(self.midata.time, "%Y%m%d-%H:%M:%S")
        self.AcTimeEdit.setDateTime(self.ac_time)

        # Set channel infos
        self.fill_channel_listView()

        self.clear_refresh(clf=True)

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
                if e.args[0] == "Empty":
                    if isinstance(self.midata, MiData):
                        self.mianno = create_new_mianno(self.midata.duration)
                    else:
                        QMessageBox.about(self, "Error",
                                          "To create a new annotation file, load a data file first.")
                        self.anno_path = ""
                        return

                if e.args[0] == "Invalid":
                    QMessageBox.about(self, "Error",
                                      r"Annotation file invalid, check "
                                      r"<a href='https://github.com/BryanWang0702/MiSleep'>MiSleep</a> for detail.")
                    self.data_path = ""
                    return
        # Set meta info
        self.AnnoPathEdit.setText(self.anno_path)

        self.clear_refresh(clf=True)

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

        self.show_idx = list(range(self.midata.n_channels))
        self.y_lims = [max(each[:1000]) for each in self.midata.signals]
        self.y_lims = [1e-3 if each == 0. else each for each in self.y_lims]
        self.y_shift = [0 for _ in range(self.midata.n_channels)]

        self.ScrollerBar.setRange(0, self.mianno.anno_length)
        self.SecondSpin.setRange(0, self.mianno.anno_length)
        self.DateTimeEdit.setDateTimeRange(self.ac_time, self.ac_time + datetime.timedelta(
            seconds=self.mianno.anno_length))

        self.hypo_ax = self.hypo_figure.subplots(nrows=1, ncols=1)

        # Set canvas for plot area
        self.SignalArea.setWidget(self.signal_canvas)
        self.HypnoArea.setWidget(self.hypo_canvas)

        self.redraw_all(second=0)
        self.clear_refresh(clf=False)

    def clear_refresh(self, clf=False):
        """Clear all plot area and refresh the canvas, clf to specify whether clear the figure"""
        if clf:
            self.signal_figure.clf()
            self.hypo_figure.clf()

        self.signal_figure.canvas.draw()
        self.signal_figure.canvas.flush_events()

        self.hypo_figure.canvas.draw()
        self.hypo_figure.canvas.flush_events()

    def plot_signals(self):
        """Main plot function, plot signal area, once replot the signal, update all figures"""
        self.signal_figure.clf()
        self.signal_ax = self.signal_figure.subplots(nrows=len(self.show_idx) + 1, ncols=1)
        # plot the spectrogram
        self.plot_spectrogram()

        for i, each in enumerate(self.show_idx):
            self.signal_ax[i + 1].plot(self.midata.signals[each][
                                       int(self.current_sec * self.midata.sf[each]):
                                       int((self.current_sec + self.show_duration) * self.midata.sf[each])],
                                       color='black', linewidth=0.5)
            y_lim = self.y_lims[each]
            y_shift = self.y_shift[each]
            self.signal_ax[i + 1].set_ylim(ymin=-y_lim + y_shift, ymax=y_lim + y_shift)
            self.signal_ax[i + 1].set_xlim(xmin=0, xmax=self.show_duration * self.midata.sf[each])
            self.signal_ax[i + 1].xaxis.set_ticks([])
            self.signal_ax[i + 1].yaxis.set_ticks([])
            self.signal_ax[i + 1].set_ylabel(f"{self.midata.channels[each]}\n\n{y_lim:.2e}")
        self.signal_ax[-1].xaxis.set_ticks([int(each * self.midata.sf[self.show_idx[-1]]) for each in
                                            range(0, self.show_duration + 1, 5)],
                                           range(self.current_sec, self.current_sec + self.show_duration + 1, 5),
                                           rotation=45)
        self.signal_ax[-1].xaxis.set_ticks([int(each * self.midata.sf[self.show_idx[-1]]) for each in
                                            range(0, self.show_duration + 1)], minor=True)

        self.signal_figure.canvas.draw()
        self.signal_figure.canvas.flush_events()

    def spec_percentile_change(self):
        """Triggered by spectrogramPercentile change"""
        self.spectrogram_percentile = self.PercentileSpin.value()
        self.plot_spectrogram(flush=True)

    def default_ch4Spec(self):
        """Set default channel for spectrogram"""
        selected_channel = [each.row() for each in self.ChListView.selectedIndexes()]
        if len(selected_channel) != 1:
            QMessageBox.about(self, "Error", "Select one channel to be the default channel for spectrogram.")
            return
        self.current_spectrogram_idx = selected_channel[0]
        self.plot_spectrogram(flush=True)

    def plot_spectrogram(self, flush=False):
        """Redraw spectrogram"""
        self.signal_ax[0].clear()
        f, t, Sxx = spectrogram(signal=self.midata.signals[self.current_spectrogram_idx][
                                       int(self.current_sec * self.midata.sf[self.current_spectrogram_idx]):
                                       int((self.current_sec + self.show_duration) * self.midata.sf[
                                           self.current_spectrogram_idx])],
                                sf=self.midata.sf[self.current_spectrogram_idx], step=1, window=1, norm=True)
        cmap = plt.cm.get_cmap('jet')

        self.signal_ax[0].set_xticks([])
        self.signal_ax[0].set_ylim(0, 30)
        self.signal_ax[0].set_ylabel(f'{self.midata.channels[self.current_spectrogram_idx]}')
        self.signal_ax[0].pcolormesh(t, f, Sxx, cmap=cmap,
                                     vmax=np.percentile(Sxx, self.spectrogram_percentile))

        if flush:
            self.signal_figure.canvas.draw()
            self.signal_figure.canvas.flush_events()

    def plot_label(self):
        """Plot label (interaction with users) in the signal area"""

    def plot_hypo(self):
        """Plot hypnogram area"""
        self.hypo_ax.clear()
        # self.hypo_axvline.remove()
        # self.hypo_axvline = self.hypo_ax.axvline(self.current_sec, color='gray', alpha=0.8)
        line_width = self.show_duration
        if self.show_duration < self.mianno.anno_length * 0.001:
            line_width = int(self.mianno.anno_length * 0.001)
        self.hypo_ax.fill_between(range(self.current_sec, self.current_sec + line_width), 0, 0.7,
                                  facecolor='red', alpha=1)
        self.hypo_ax.step(range(self.mianno.anno_length), self.mianno.sleep_state, where='mid', linewidth=1)
        self.hypo_ax.set_ylim(0, 4.5)
        self.hypo_ax.set_xlim(0, self.mianno.anno_length)
        self.hypo_ax.yaxis.set_ticks([1, 2, 3, 4], ['NREM', 'REM', 'Wake', 'INIT'])

        self.hypo_figure.canvas.draw()
        self.hypo_figure.canvas.flush_events()

    def redraw_all(self, second=0):
        """Second validation and Redraw all"""
        if second + self.show_duration >= self.mianno.anno_length:
            self.current_sec = self.mianno.anno_length - self.show_duration
        elif second <= 0:
            self.current_sec = 0
        else:
            self.current_sec = second

        # These 3 set functions will call the value change operation in cycle, stop first
        self.ScrollerBar.setValue(self.current_sec)
        self.SecondSpin.setValue(self.current_sec)
        self.DateTimeEdit.setDateTime(self.ac_time + datetime.timedelta(seconds=self.current_sec))
        self.plot_signals()
        self.plot_hypo()
        self.plot_label()

    def fill_channel_listView(self):
        """Fill channel listView with self.midata.channels"""
        self.channel_slm.setStringList(self.midata.channels)
        self.ChListView.setModel(self.channel_slm)

    def click_signal(self):
        """Click the signal area and add marker or start_end label, triggered by button_release_event"""

    def click_hypo(self, event):
        """Click hypnogram and jump to the time"""
        current_sec = int(event.xdata)
        self.redraw_all(second=current_sec)

    def scroller_change(self):
        """ScrollerBar value changed"""
        current_sec = self.ScrollerBar.value()
        self.redraw_all(second=current_sec)

    def SecondSpin_change(self):
        """SecondSpin changed"""
        current_sec = self.SecondSpin.value()
        self.redraw_all(second=current_sec)

    def DateTimeEdit_change(self):
        """DateTimeEdit changed, jump to the time"""
        dateTime = self.DateTimeEdit.dateTime().toPyDateTime()
        current_sec = int((dateTime - self.ac_time).total_seconds())
        self.redraw_all(second=current_sec)

    def show_chs(self):
        """show selected channels"""
        selected_channels = [each.row() for each in self.ChListView.selectedIndexes()]
        if not selected_channels:
            return
        self.show_idx = sorted(selected_channels)
        self.plot_signals()

    def hide_chs(self):
        """Hide selected channels"""
        selected_channels = [each.row() for each in self.ChListView.selectedIndexes()]
        if not selected_channels:
            return
        all_channels = copy.deepcopy(self.show_idx)
        for each in selected_channels:
            if each in all_channels:
                all_channels.remove(each)

        if not all_channels:
            QMessageBox.about(self, "Error", "You can't hide all channels!")
            return

        self.show_idx = all_channels
        self.plot_signals()

    def delete_chs(self):
        """Delete selected channels"""
        selected_channel = [each.row() for each in self.ChListView.selectedIndexes()]
        if not selected_channel:
            return
        box = QMessageBox.question(self, 'Warning', 'You are deleting data!',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if box == QMessageBox.Yes:

            if len(selected_channel) == self.midata.n_channels:
                QMessageBox.about(self, "Error", "You can't delete all channels!")
                return

            spec_name = self.midata.channels[self.current_spectrogram_idx]
            for each in sorted(selected_channel, reverse=True):
                # Mark the deleted position
                self.y_lims[each] = -1
                self.y_shift[each] = -1
                self.midata.delete(self.midata.channels[each])

            # Recover the y_lims, y_shift and spec_idx
            self.y_lims = [each for each in self.y_lims if each != -1]
            self.y_shift = [each for each in self.y_shift if each != -1]
            if spec_name in self.midata.channels:
                self.current_spectrogram_idx = self.midata.channels.index(spec_name)
            else:
                self.current_spectrogram_idx = 0

            self.show_idx = list(range(self.midata.n_channels))
            self.fill_channel_listView()
            self.redraw_all(second=self.current_sec)

    def scaler_up(self):
        """Adjust selected channels' scaler, triggered by ScalerUpBt"""
        selected_channel = [each.row() for each in self.ChListView.selectedIndexes()]
        if not selected_channel:
            return

        self.y_lims = [lim * 0.9 if idx in selected_channel else lim for idx, lim in enumerate(self.y_lims)]
        self.plot_signals()

    def scaler_down(self):
        """Scaler down, triggered by ScalerDownBt"""
        selected_channel = [each.row() for each in self.ChListView.selectedIndexes()]
        if not selected_channel:
            return

        self.y_lims = [lim * 1.1 if idx in selected_channel else lim for idx, lim in enumerate(self.y_lims)]
        self.plot_signals()

    def shift_up(self):
        """Shift up selected channel"""
        selected_channel = [each.row() for each in self.ChListView.selectedIndexes()]
        if not selected_channel:
            return
        self.y_shift = [shift - self.y_lims[idx] * 0.05 if idx in selected_channel else shift for idx, shift in
                        enumerate(self.y_shift)]
        self.plot_signals()

    def shift_down(self):
        """Shift down selected channel"""
        selected_channel = [each.row() for each in self.ChListView.selectedIndexes()]
        if not selected_channel:
            return
        self.y_shift = [shift + self.y_lims[idx] * 0.05 if idx in selected_channel else shift for idx, shift in
                        enumerate(self.y_shift)]
        self.plot_signals()

    def set_show_duration(self, type_='Combo'):
        """Set show_duration with ShowRangeCombo or EpochNumSpin"""

        if type_ == 'Combo':
            selected_idx = self.ShowRangeCombo.currentIndex()
            if self.ShowRangeCombo_dict[selected_idx] + self.current_sec >= self.mianno.anno_length:
                self.show_duration = 30
                self.current_sec = 0
                self.ShowRangeCombo.setCurrentIndex(0)
            else:
                self.show_duration = self.ShowRangeCombo_dict[selected_idx]
        if type_ == 'Spin':
            show_duration = self.EpochNumSpin.value() * self.epoch_length
            if show_duration + self.current_sec >= self.mianno.anno_length:
                self.show_duration = 30
                self.current_sec = 0
                self.EpochNumSpin.setValue(6)
            else:
                self.show_duration = show_duration

        self.redraw_all(second=self.current_sec)
        self.ScrollerBar.setPageStep(self.show_duration)

    def CustomSecondCheck_clicked(self):
        """If CustomSecondCheck was clicked"""
        if self.CustomSecondsCheck.isChecked():
            self.ShowRangeCombo.setDisabled(True)
            self.EpochNumSpin.setEnabled(True)
            self.set_show_duration(type_='Spin')
        else:
            self.ShowRangeCombo.setEnabled(True)
            self.EpochNumSpin.setDisabled(True)
            self.set_show_duration(type_='Combo')

    def ShowRangeCombo_changed(self):
        """Triggered by ShowRangeCombo index change"""
        self.set_show_duration(type_='Combo')

    def EpochNumSpin_changed(self):
        """Triggered by EpochNumSpin value change"""
        self.set_show_duration(type_='Spin')

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
