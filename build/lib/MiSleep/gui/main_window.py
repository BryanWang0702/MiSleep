# -*- coding: UTF-8 -*-
"""
@Project: MiSleep_v2
@File: main_window.py
@Author: Xueqiang Wang
@Date: 2024/3/8
@Description:  Main window of MiSleep gui, all plot business is based on 
                annotations.
"""
import copy
import datetime
import configparser
import json

import numpy as np
from PyQt5.QtCore import QCoreApplication, Qt, QStringListModel
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QAction, QShortcut
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from misleep.preprocessing.spectral import spectrogram
from misleep.io.base import MiData, MiAnnotation
from misleep.io.signal_io import load_mat, load_edf
from misleep.io.annotation_io import load_misleep_anno
from misleep.gui.utils import create_new_mianno
from misleep.utils.annotation import lst2group
from misleep.gui.about import about_dialog
from misleep.gui.label_dialog import label_dialog
from misleep.gui.spec_window import SpecWindow
from misleep.gui.uis.main_window_ui import Ui_MiSleep
from misleep.preprocessing.spectral import spectrogram, spectrum, band_power
from misleep.gui.thread import SaveThread


class main_window(QMainWindow, Ui_MiSleep):
    def __init__(self, parent=None):
        """
        Initialize the Main Window of MiSleep, load data in the toolBar area
        """
        super().__init__(parent)

        # Enable high dpi devices
        QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        self.setupUi(self)

        # Load configuration
        self.config = configparser.ConfigParser()
        self.config.read(r'./misleep/config.ini')

        # print(f'{self.config['gui']['openpath']}')
        self.midata = None
        self.mianno = None

        # original data and label file path
        self.data_path = ""
        self.anno_path = ""

        # Set initial params
        self.current_sec = 0
        self.show_duration = 30  # Seconds of duration to plot
        self.total_seconds = 0  # Total seconds for plot
        self.y_lims = None  # list of y lim for each channel
        self.y_shift = None  # list of y shift for each channel
        self.show_idx = None  # Channels to show in plot area
        self.state_map_dict = {int(key): value for key, value 
                               in json.loads(self.config['gui']['statemap']).items()}
        self.state_color_dict = {int(key): value for key, value 
                               in json.loads(self.config['gui']['statecolor']).items()}
        self.ShowRangeCombo_dict = {0: 30, 1: 60, 2: 300, 3: 1800, 4: 3600}
        self.FilterTypeCombo_dict = {
            0: "bandpass",
            1: "highpass",
            2: "lowpass",
            3: "bandstop",
        }
        self.current_spectrogram_idx = 0
        self.spectrogram_percentile = 99.7
        self.show_midata = None
        self.epoch_length = 5
        self.ac_time = None

        # Default marker label and start_end label for label dialog
        # self.marker_label = ['Injection', 'Pat', 'Add water', 'label', 'label']
        # self.start_end_label = ['Spindle', 'Slow wave activity', 'start_end_label']
        # self.marker_label = json.loads(self.config['gui']['MARKERS'])
        # self.start_end_label = json.loads(self.config['gui']['STARTEND'])

        # Signal area figure
        self.signal_figure = plt.figure()
        self.signal_ax = self.signal_figure.subplots()
        self.signal_figure.set_tight_layout(True)
        self.signal_figure.tight_layout(h_pad=0, w_pad=0)
        self.signal_figure.subplots_adjust(hspace=0)  # Adjust subplots
        self.signal_canvas = FigureCanvas(self.signal_figure)
        # Add button click release event for signal canvas
        self.signal_canvas.mpl_connect("button_release_event", self.click_signal)
        # start and end axvline, only two lines
        self.signal_start_end_axvline = []
        self.signal_marker_axvline = []

        # Start-end for labels
        self.start_end = []
        # Start-end for milliseconds, for start_end label
        self.start_end_ms = []

        # Hypnogram area figure
        self.hypo_figure = plt.figure(layout="constrained")
        self.hypo_ax = self.hypo_figure.subplots()
        self.hypo_canvas = FigureCanvas(self.hypo_figure)
        self.hypo_canvas.mpl_connect("button_release_event", self.click_hypo)
        self.hypo_axvline = self.hypo_ax.axvline(
            self.current_sec, color="gray", alpha=0.8
        )

        # Initial params for widgets
        self.channel_slm = QStringListModel()

        # Initial about dialog and spec window
        self.about_dialog = about_dialog(version=json.loads(self.config['gui']['version']),
                                         update_time=json.loads(self.config['gui']['updatetime']))
        self.spec_window = SpecWindow()
        # Initial label dialog
        self.label_dialog = label_dialog(config=self.config)

        # Check wheher operation done and saved or not
        self.is_saved = True

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
        # Channel name change
        self.channel_slm.dataChanged.connect(self.channel_rename)

        # Filter
        self.FilterTypeCombo.currentIndexChanged.connect(self.FilterTypeCombo_change)
        self.FilterConfirmBt.clicked.connect(self.filter_confirm)

        # PlotSpecBt
        self.PlotSpecBt.clicked.connect(self.show_spec_window)

        # Custom second spin edit and ShowRangeCombo
        self.ShowRangeCombo.setEnabled(True)
        self.EpochNumSpin.setDisabled(True)
        self.EpochNumSpin.setRange(1, 720)
        self.EpochNumSpin.setValue(6)
        self.EpochNumSpin.valueChanged.connect(self.EpochNumSpin_changed)
        self.ShowRangeCombo.currentIndexChanged.connect(self.ShowRangeCombo_changed)
        self.CustomSecondsCheck.clicked.connect(self.CustomSecondCheck_clicked)

        # Label radio check start_end by default
        self.SleepStateRadio.setChecked(True)
        self.SleepStateRadio.toggled.connect(lambda: self.radio_recheck(self.SleepStateRadio))
        self.StartEndRadio.toggled.connect(lambda: self.radio_recheck(self.StartEndRadio))
        # self.SleepStateRadio.toggled.connect(lambda: self.radio_recheck(self.SleepStateRadio))

        # Label button
        self.NREMBt.clicked.connect(self.nrem_label)
        self.REMBt.clicked.connect(self.rem_label)
        self.WakeBt.clicked.connect(self.wake_label)
        self.InitBt.clicked.connect(self.init_label)
        self.LabelBt.clicked.connect(self.append_start_end)

        # Label button shortcut
        self.nremSc = QShortcut(QKeySequence('1'), self)
        self.nremSc.activated.connect(self.nrem_label)
        self.remSc = QShortcut(QKeySequence('2'), self)
        self.remSc.activated.connect(self.rem_label)
        self.wakeSc = QShortcut(QKeySequence('3'), self)
        self.wakeSc.activated.connect(self.wake_label)
        self.initSc = QShortcut(QKeySequence('4'), self)
        self.initSc.activated.connect(self.init_label)

        # save labels
        self.SaveLabelBt.clicked.connect(self.save_anno)

    def load_data(self):
        """Triggered by actionLoad_Data, get MiData"""
        data_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select data file",
            f"{self.config['gui']['openpath']}",
            "Matlab Files (*.mat *.MAT);;EDF Files (*.edf *.EDF)",
        )

        if data_path == "":
            return
        self.data_path = data_path
        if self.data_path.endswith((".mat", ".MAT")):
            self.midata = load_mat(data_path=self.data_path)
            if self.midata is None:
                QMessageBox.about(
                    self,
                    "Error",
                    r"Data file invalid, check "
                    r"<a href='https://github.com/BryanWang0702/MiSleep'>MiSleep</a> for detail.",
                )
                self.data_path = ""
                return

        if self.data_path.endswith((".edf", ".EDF")):
            try:
                self.midata = load_edf(data_path=self.data_path)
            except Exception:
                QMessageBox.about(
                    self,
                    "Error",
                    r"Data file invalid, check "
                    r"<a href='https://github.com/BryanWang0702/MiSleep'>MiSleep</a> for detail.",
                )
                self.data_path = ""
                return

        # Save config
        self.save_config({'openpath': self.data_path})

        # Set meta info
        self.DataPathEdit.setText(self.data_path)
        self.ac_time = datetime.datetime.strptime(self.midata.time, 
                                                  "%Y%m%d-%H:%M:%S")
        self.AcTimeEdit.setDateTime(self.ac_time)

        # Set channel infos
        self.fill_channel_listView()

        self.start_end = []
        self.clear_refresh(clf=True)

    def load_anno(self):
        """Triggered by actionLoad_Annotation"""
        anno_path, _ = QFileDialog.getOpenFileName(
            self, "Select annotation file", 
            f"{self.config['gui']['openpath']}", 
            "txt Files (*.txt *.TXT)"
        )

        if anno_path == "":
            return
        self.anno_path = anno_path

        if self.anno_path.endswith((".txt", ".TXT")):
            try:
                self.mianno = load_misleep_anno(self.anno_path)
            except AssertionError as e:
                if e.args[0] == "Empty":
                    if isinstance(self.midata, MiData):
                        self.mianno = create_new_mianno(self.midata.duration)
                    else:
                        QMessageBox.about(
                            self,
                            "Error",
                            "To create a new annotation file, load a data file first.",
                        )
                        self.anno_path = ""
                        return

                if e.args[0] == "Invalid":
                    QMessageBox.about(
                        self,
                        "Error",
                        r"Annotation file invalid, check "
                        r"<a href='https://github.com/BryanWang0702/MiSleep'>MiSleep</a> for detail.",
                    )
                    self.data_path = ""
                    return
                
        # Save config
        self.save_config({'openpath': self.anno_path})

        # Set meta info
        self.AnnoPathEdit.setText(self.anno_path)
        self.start_end = []
        self.clear_refresh(clf=True)

    def check_show(self):
        """Check and show all, triggered by actionShow"""
        if not isinstance(self.midata, MiData) or not isinstance(
            self.mianno, MiAnnotation
        ):
            QMessageBox.about(
                self, "Error", r"Load data file and annotation file first."
            )
            return

        self.show_idx = list(range(self.midata.n_channels))
        self.y_lims = [max(each[:1000]) for each in self.midata.signals]
        self.y_lims = [1e-3 if each == 0.0 else each for each in self.y_lims]
        self.y_shift = [0 for _ in range(self.midata.n_channels)]

        self.total_seconds = self.midata.duration if self.midata.duration < self.mianno.anno_length else self.mianno.anno_length
        self.reset_sec_limit()

        self.hypo_ax = self.hypo_figure.subplots(nrows=1, ncols=1)

        # Set canvas for plot area
        self.SignalArea.setWidget(self.signal_canvas)
        self.HypnoArea.setWidget(self.hypo_canvas)

        self.redraw_all(second=0)
        self.clear_refresh(clf=False)

    def reset_sec_limit(self):
        """When show duration changes, change the limitation of 
        ScrollerBar, DateTimeEdit, SecondSpin
        """
        self.ScrollerBar.setRange(0, self.total_seconds-self.show_duration)
        self.SecondSpin.setRange(0, self.total_seconds-self.show_duration)

        # Prevent DateTimeEdit change
        self.DateTimeEdit.blockSignals(True)
        self.DateTimeEdit.setDateTimeRange(
            self.ac_time,
            self.ac_time + datetime.timedelta(seconds=self.total_seconds-self.show_duration),
        )
        self.DateTimeEdit.blockSignals(False)

    def clear_refresh(self, clf=False):
        """Clear all plot area and refresh the canvas, clf to specify whether clear the figure"""
        if clf:
            self.signal_figure.clf()
            self.hypo_figure.clf()

        self.hypo_figure.canvas.draw()
        self.hypo_figure.canvas.flush_events()
        self.signal_figure.canvas.draw()
        self.signal_figure.canvas.flush_events()

    def plot_signals(self, flush=True, clf=True, replot_axes=None):
        """Main plot function, plot signal area, once replot the signal, 
        update all figures
        
        Parameters
        ----------
        flush : bool, optional
            Whether to flush the signal area
        clf : bool, optional
            Clear the figure or not. If not, clear the axes
        replot_axes : list of int, optional
            Only replot specifed axes (channels), when shift up/down, 
            scalar up/down and so on
        """

        if clf:
            self.signal_figure.clf()
            self.signal_ax = self.signal_figure.subplots(
                nrows=len(self.show_idx) + 1, ncols=1)
            # plot the spectrogram
            self.plot_spectrogram()

        # Get label
        sleep_state = self.mianno.sleep_state[
            self.current_sec : self.current_sec + self.show_duration + 1
        ]
        sleep_state = lst2group([i, each] for i, each in enumerate(sleep_state))

        for i, each in enumerate(self.show_idx):
            if replot_axes is not None and each not in replot_axes:
                continue
            y_lim = self.y_lims[each]
            y_shift = self.y_shift[each]

            # if didn't clear the figure, clear the axes
            if not clf:
                self.signal_ax[i + 1].clear()

            self.signal_ax[i + 1].plot(
                self.midata.signals[each][
                    int(self.current_sec * self.midata.sf[each]) : int(
                        (self.current_sec + self.show_duration) * self.midata.sf[each]
                    )
                ],
                color="black",
                linewidth=0.5,
            )
            self.signal_ax[i + 1].set_ylim(ymin=-y_lim + y_shift, ymax=y_lim + y_shift)
            self.signal_ax[i + 1].set_xlim(
                xmin=0, xmax=self.show_duration * self.midata.sf[each]
            )
            self.signal_ax[i + 1].xaxis.set_ticks([])
            self.signal_ax[i + 1].yaxis.set_ticks([])
            self.signal_ax[i + 1].set_ylabel(
                f"{self.midata.channels[each]}\n\n{y_lim:.2e}"
            )

            # plot label
            for state in sleep_state:
                self.signal_ax[i + 1].fill_between(
                    range(
                        int(state[0] * self.midata.sf[each]),
                        int((state[1] + 1) * self.midata.sf[each]),
                    ),
                    -y_lim + y_shift,
                    y_lim + y_shift,
                    facecolor=self.state_color_dict[state[2]],
                    alpha=0.1,
                )
        self.signal_ax[-1].xaxis.set_ticks(
            [
                int(each * self.midata.sf[self.show_idx[-1]])
                for each in range(0, self.show_duration + 1, 5)
            ],
            range(self.current_sec, self.current_sec + self.show_duration + 1, 5),
            rotation=45,
        )
        self.signal_ax[-1].xaxis.set_ticks(
            [
                int(each * self.midata.sf[self.show_idx[-1]])
                for each in range(0, self.show_duration + 1)
            ],
            minor=True,
        )

        if self.StartEndRadio.isChecked():
            self.plot_start_end_line(flush=False, ms=True)
        if self.SleepStateRadio.isChecked():
            self.plot_start_end_line(flush=False)
        self.plot_marker_line(flush=False)
        self.plot_start_end_label_line(flush=False)

        if flush:
            self.signal_figure.canvas.draw()
            self.signal_figure.canvas.flush_events()

    def replot_sleep_state_bg(self, state):
        """Replot the sleep state if confirmed by using start_end area"""
        # Check the start_end and current_sec overlap area
        replot_start = 0 if \
            self.current_sec >= self.start_end[0] else \
            (self.start_end[0] - self.current_sec)
        replot_end = self.show_duration if (
            self.current_sec + self.show_duration
            <= self.start_end[1]
        ) else (self.start_end[1] - self.current_sec)
                       
        for i, each in enumerate(self.show_idx):
            y_lim = self.y_lims[each]
            y_shift = self.y_shift[each]
            self.signal_ax[i + 1].fill_between(
                    range(
                        int(replot_start * self.midata.sf[each]),
                        int(replot_end * self.midata.sf[each]),
                    ),
                    -y_lim + y_shift,
                    y_lim + y_shift,
                    facecolor="white",
                    alpha=1,
                )
            self.signal_ax[i + 1].fill_between(
                    range(
                        int(replot_start * self.midata.sf[each]),
                        int(replot_end * self.midata.sf[each]),
                    ),
                    -y_lim + y_shift,
                    y_lim + y_shift,
                    facecolor=self.state_color_dict[state],
                    alpha=0.1,
                )
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
            QMessageBox.about(
                self,
                "Error",
                "Select one channel to be the default channel for spectrogram.",
            )
            return
        self.current_spectrogram_idx = selected_channel[0]
        self.plot_spectrogram(flush=True)

    def plot_spectrogram(self, flush=False):
        """Redraw spectrogram"""
        self.signal_ax[0].clear()
        f, t, Sxx = spectrogram(
            signal=self.midata.signals[self.current_spectrogram_idx][
                int(
                    self.current_sec * self.midata.sf[self.current_spectrogram_idx]
                ) : int(
                    (self.current_sec + self.show_duration)
                    * self.midata.sf[self.current_spectrogram_idx]
                )
            ],
            sf=self.midata.sf[self.current_spectrogram_idx],
            step=1,
            window=1,
            norm=True,
        )
        cmap = plt.cm.get_cmap("jet")

        self.signal_ax[0].set_xticks([])
        self.signal_ax[0].set_ylim(0, 30)
        self.signal_ax[0].set_ylabel(
            f"{self.midata.channels[self.current_spectrogram_idx]}"
        )
        self.signal_ax[0].pcolormesh(
            t, f, Sxx, cmap=cmap, vmax=np.percentile(Sxx, self.spectrogram_percentile)
        )

        if flush:
            self.signal_figure.canvas.draw()
            self.signal_figure.canvas.flush_events()

    def plot_start_end_line(self, flush=True, ms=False):
        """Plot start_end lime line (interaction with users) in the signal area"""

        if ms:
            start_end = self.start_end_ms
        else:
            start_end = self.start_end
        # self.plot_signals(flush=False)
        for axvline in self.signal_start_end_axvline:
            try:
                axvline.remove()
            except:
                pass
        self.signal_start_end_axvline = []
        for i, each in enumerate(start_end):
            if self.current_sec <= each <= self.current_sec + self.show_duration:
                for idx, show_ in enumerate(self.show_idx):
                    y_lim = self.y_lims[show_]
                    y_shift = self.y_shift[show_]
                    if ms:
                        x = round((each - self.current_sec) * self.midata.sf[show_], 3)
                    if not ms:
                        x = int((each - self.current_sec) * self.midata.sf[show_])
                        
                    if i == 0:
                        self.signal_start_end_axvline.append(
                            self.signal_ax[idx + 1].axvline(
                                x,
                                color="lime",
                                alpha=1,
                            )
                        )
                        
                    if i == 1:
                        self.signal_start_end_axvline.append(
                            self.signal_ax[idx + 1].axvline(
                                x,
                                color="lime",
                                alpha=1,
                            )
                        )
                        
                if i == 0:
                    self.signal_start_end_axvline.append(
                            self.signal_ax[idx+1].text(
                                x=x,
                                y=-y_lim + y_shift,
                                s="S",
                                color="lime",
                            )
                        )
                if i == 1:
                    self.signal_start_end_axvline.append(
                            self.signal_ax[idx+1].text(
                                x=x,
                                y=-y_lim + y_shift,
                                horizontalalignment="right",
                                s="E",
                                color="lime",
                            )
                        )

        if flush:
            self.signal_figure.canvas.draw()
            self.signal_figure.canvas.flush_events()

            self.plot_hypo()

    def plot_marker_line(self, flush=True):
        """Plot marker line in the signal area with clicking"""
        for axvline in self.signal_marker_axvline:
            try:
                axvline.remove()
            except:
                pass
        self.signal_marker_axvline = []
        for each in self.mianno.marker:
            if self.current_sec <= each[0] <= self.current_sec + self.show_duration:
                for idx, show_ in enumerate(self.show_idx):
                    self.signal_marker_axvline.append(
                        self.signal_ax[idx + 1].axvline(
                        int((each[0] - self.current_sec) * self.midata.sf[show_]),
                        color="Red",
                        alpha=1,
                    ))
                self.signal_marker_axvline.append(
                    self.signal_ax[1].text(
                    x=int((each[0] - self.current_sec) * self.midata.sf[show_]),
                    y=self.y_lims[self.show_idx[0]] + self.y_shift[self.show_idx[1]],
                    s=each[1],
                    verticalalignment="top",
                    color="Red",
                ))
        
        if flush:
            self.signal_figure.canvas.draw()
            self.signal_figure.canvas.flush_events()
            self.plot_hypo()

    def plot_start_end_label_line(self, flush=True):
        """Plot miannotation's start_end label line"""
        for each in self.mianno.start_end:
            if self.current_sec <= each[0] <= self.current_sec + self.show_duration:
                for idx, show_ in enumerate(self.show_idx):
                    self.signal_ax[idx + 1].axvline(
                        int((each[0] - self.current_sec) * self.midata.sf[show_]),
                        color="blue",
                        alpha=1,
                    )
                self.signal_ax[1].text(
                    x=int((each[0] - self.current_sec) * self.midata.sf[show_]),
                    y=self.y_lims[self.show_idx[0]] + self.y_shift[self.show_idx[1]],
                    s=each[2]+'-S',
                    verticalalignment="top",
                    color="blue",
                )

            if self.current_sec <= each[1] <= self.current_sec + self.show_duration:
                for idx, show_ in enumerate(self.show_idx):
                    self.signal_ax[idx + 1].axvline(
                        int((each[1] - self.current_sec) * self.midata.sf[show_]),
                        color="blue",
                        alpha=1,
                    )
                self.signal_ax[1].text(
                    x=int((each[1] - self.current_sec) * self.midata.sf[show_]),
                    y=self.y_lims[self.show_idx[0]] + self.y_shift[self.show_idx[1]],
                    s=each[2]+'-E',
                    verticalalignment="top",
                    horizontalalignment='right',
                    color="blue",
                )

        if flush:
            self.signal_figure.canvas.draw()
            self.signal_figure.canvas.flush_events()

    def plot_hypo(self):
        """Plot hypnogram area"""
        self.hypo_ax.clear()
        self.hypo_axvline.remove()
        self.hypo_axvline = self.hypo_ax.axvline(
            self.current_sec, color="gray", alpha=0.8
        )
        self.hypo_ax.step(
            range(self.mianno.anno_length),
            self.mianno.sleep_state,
            where="mid",
            linewidth=1,
        )
        self.hypo_ax.set_ylim(0, 4.5)
        self.hypo_ax.set_xlim(0, self.total_seconds)
        self.hypo_ax.yaxis.set_ticks([1, 2, 3, 4], ["NREM", "REM", "Wake", "INIT"])
        if self.StartEndRadio.isChecked():
            for each in self.start_end_ms:
                self.hypo_ax.axvline(each, color="lime", alpha=1)

        if self.SleepStateRadio.isChecked():
            for each in self.start_end:
                self.hypo_ax.axvline(each, color="lime", alpha=1)

        for each in self.mianno.marker:
            self.hypo_ax.axvline(each[0], color="Red", alpha=1)

        self.hypo_figure.canvas.draw()
        self.hypo_figure.canvas.flush_events()

    def redraw_all(self, second=0):
        """Second validation and Redraw all"""
        if second + self.show_duration >= self.total_seconds:
            self.current_sec = self.total_seconds - self.show_duration
        elif second <= 0:
            self.current_sec = 0
        else:
            self.current_sec = second

        # These 3 set functions will call the value change operation in cycle, stop first
        self.ScrollerBar.blockSignals(True)
        self.SecondSpin.blockSignals(True)
        self.DateTimeEdit.blockSignals(True)
        self.ScrollerBar.setValue(self.current_sec)
        self.SecondSpin.setValue(self.current_sec)
        self.DateTimeEdit.setDateTime(
            self.ac_time + datetime.timedelta(seconds=self.current_sec)
        )
        self.ScrollerBar.blockSignals(False)
        self.SecondSpin.blockSignals(False)
        self.DateTimeEdit.blockSignals(False)
        self.plot_signals()
        self.plot_hypo()

    def fill_channel_listView(self):
        """Fill channel listView with self.midata.channels"""
        self.channel_slm.setStringList(self.midata.channels)
        self.ChListView.setModel(self.channel_slm)

    def radio_recheck(self, radioBt):
        """Check which radio was checked in the label area"""
        if radioBt.text() == "Sleep state":
            self.start_end_ms = []
            self.plot_start_end_line()
        if radioBt.text() == "Start-End":
            self.start_end = []
            self.plot_start_end_line(ms=True)

    def click_signal(self, event):
        """Click the signal area and add marker or start_end label, triggered by button_release_event"""
        if event.inaxes == self.signal_ax[0]:
            return

        try:
            sec = (
                int(event.xdata / self.midata.sf[
                        self.show_idx[np.where(self.signal_ax == event.inaxes)[0][0] - 1]
                    ]
                )
                + self.current_sec
            )
        except TypeError:
            return

        if self.SleepStateRadio.isChecked():
            if event.button == 3:
                # Mouse right click, cancel the exist line(s)
                for each in self.mianno.start_end:
                    if each[0] == sec or each[1] == sec:
                        self.mianno.start_end.remove(each)
                        self.plot_signals()
                        return
                if len(self.start_end) == 0:
                    return
                if len(self.start_end) >= 1 and sec == self.start_end[0]:
                    self.start_end = []
                    self.plot_start_end_line()
                    return
                if len(self.start_end) == 2 and sec+1 == self.start_end[1]:
                    self.start_end.pop(1)
                    self.plot_start_end_line()
                    return

                return
                 
            if not self.start_end:
                self.start_end.append(sec)
            elif len(self.start_end) == 2:
                # Clear start end label
                self.start_end = []
                self.start_end.append(sec)
            else:
                if sec < self.start_end[0]:
                    QMessageBox.about(self, "Error", "End should be larger than Start!")
                    return
                self.start_end.append(sec + 1)

            self.plot_start_end_line()

        if self.MarkerRadio.isChecked():
            if event.button == 3:
                for each in self.mianno.marker:
                    if each[0] == sec:
                        self.mianno.marker.remove(each)
                        self.plot_signals()
                        self.plot_hypo()
                return
            
            self.label_dialog._type = 0
            self.label_dialog.show_contents()
            self.label_dialog.exec_()
            if self.label_dialog.closed:
                return
            
            label_name = self.label_dialog.label_name

            # Add marker label
            self.mianno.marker.append([sec, label_name])

            self.plot_marker_line()
        
            self.is_saved = False

        if self.StartEndRadio.isChecked():
            x = round(event.xdata / self.midata.sf[
                        self.show_idx[np.where(self.signal_ax == event.inaxes)[0][0] - 1]
                    ]
                , 3) + self.current_sec
            # start end ms 
            if event.button == 3:
                # Mouse right click, cancel the exist line(s)
                for each in self.mianno.start_end:
                    if int(each[0]) == sec or int(each[1]) == sec:
                        self.mianno.start_end.remove(each)
                        self.plot_signals()
                        return
                if len(self.start_end_ms) == 0:
                    return
                if len(self.start_end_ms) >= 1 and sec == int(self.start_end_ms[0]):
                    self.start_end_ms = []
                    self.plot_start_end_line(ms=True)
                    return
                if len(self.start_end_ms) == 2 and sec == int(self.start_end_ms[1]):
                    self.start_end_ms.pop(1)
                    self.plot_start_end_line(ms=True)
                    return

                return
                 
            if not self.start_end_ms:
                self.start_end_ms.append(x)
            elif len(self.start_end_ms) == 2:
                # Clear start end label
                self.start_end_ms = []
                self.start_end_ms.append(x)
            else:
                if x < self.start_end_ms[0]:
                    QMessageBox.about(self, "Error", "End should be larger than Start!")
                    return
                self.start_end_ms.append(x)

            self.plot_start_end_line(ms=True)

    def click_hypo(self, event):
        """Click hypnogram and jump to the time"""
        current_sec = int(event.xdata)
        self.redraw_all(second=current_sec)

    def scroller_change(self):
        """ScrollerBar value changed"""
        self.ScrollerBar.setDisabled(True)
        current_sec = self.ScrollerBar.value()
        self.redraw_all(second=current_sec)
        self.ScrollerBar.setEnabled(True)

    def SecondSpin_change(self):
        """SecondSpin changed"""
        current_sec = self.SecondSpin.value()
        self.redraw_all(second=current_sec)

    def DateTimeEdit_change(self):
        """DateTimeEdit changed, jump to the time"""
        dateTime = self.DateTimeEdit.dateTime().toPyDateTime()
        current_sec = int((dateTime - self.ac_time).total_seconds())
        self.redraw_all(second=current_sec)

    def channel_rename(self):
        """Channel rename"""
        new_channels = self.channel_slm.stringList()
        for idx, each in enumerate(self.midata.channels):
            if each != new_channels[idx]:
                self.midata.rename_channels({each: new_channels[idx]})
        self.fill_channel_listView()
        self.plot_signals()

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
        box = QMessageBox.question(
            self,
            "Warning",
            "You are deleting data!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

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

        self.y_lims = [
            lim * 0.9 if idx in selected_channel else lim
            for idx, lim in enumerate(self.y_lims)
        ]
        self.plot_signals(clf=False, replot_axes=selected_channel)

    def scaler_down(self):
        """Scaler down, triggered by ScalerDownBt"""
        selected_channel = [each.row() for each in self.ChListView.selectedIndexes()]
        if not selected_channel:
            return

        self.y_lims = [
            lim * 1.1 if idx in selected_channel else lim
            for idx, lim in enumerate(self.y_lims)
        ]
        self.plot_signals(clf=False, replot_axes=selected_channel)

    def shift_up(self):
        """Shift up selected channel"""
        selected_channel = [each.row() for each in self.ChListView.selectedIndexes()]
        if not selected_channel:
            return
        self.y_shift = [
            shift - self.y_lims[idx] * 0.05 if idx in selected_channel else shift
            for idx, shift in enumerate(self.y_shift)
        ]
        self.plot_signals(clf=False, replot_axes=selected_channel)

    def shift_down(self):
        """Shift down selected channel"""
        selected_channel = [each.row() for each in self.ChListView.selectedIndexes()]
        if not selected_channel:
            return
        self.y_shift = [
            shift + self.y_lims[idx] * 0.05 if idx in selected_channel else shift
            for idx, shift in enumerate(self.y_shift)
        ]
        self.plot_signals(clf=False, replot_axes=selected_channel)

    def filter_confirm(self):
        """Filter operations, triggered by FilterConfirmBt"""
        selected_channel = [each.row() for each in self.ChListView.selectedIndexes()]
        if not selected_channel:
            return
        if len(selected_channel) > 1:
            QMessageBox.about(
                self,
                "Error",
                "Select one channel to be the default channel for spectrogram.",
            )
            return

        filter_type = self.FilterTypeCombo_dict[self.FilterTypeCombo.currentIndex()]
        low = self.FilterLowSpin.value()
        high = self.FilterHighSpin.value()
        if filter_type == "bandpass" or filter_type == "bandstop":
            if low >= high:
                return
        self.midata.filter(
            chans=[self.midata.channels[selected_channel[0]]],
            btype=filter_type,
            low=low,
            high=high,
        )
        self.y_lims.append(self.y_lims[selected_channel[0]])
        self.y_shift.append(self.y_shift[selected_channel[0]])

        self.show_idx.append(self.midata.n_channels - 1)
        self.fill_channel_listView()
        self.redraw_all(second=self.current_sec)

    def FilterTypeCombo_change(self):
        """FilterTypeCombo changed"""
        if (
            self.FilterTypeCombo.currentIndex() == 0
            or self.FilterTypeCombo.currentIndex() == 3
        ):
            self.FilterHighSpin.setEnabled(True)
            self.FilterLowSpin.setEnabled(True)
        if self.FilterTypeCombo.currentIndex() == 1:
            self.FilterHighSpin.setDisabled(True)
            self.FilterLowSpin.setEnabled(True)
        if self.FilterTypeCombo.currentIndex() == 2:
            self.FilterHighSpin.setEnabled(True)
            self.FilterLowSpin.setDisabled(True)

    def show_spec_window(self):
        """Show spectrum dialog, triggered by PlotSpecBt"""
        if len(self.start_end) != 2 or self.start_end[1] - self.start_end[0] < 10:
            QMessageBox.about(
                self,
                "Error",
                "Please select a start-end larger than 10 seconds.",
            )
            return
        
        selected_channel = [each.row() for each in self.ChListView.selectedIndexes()]

        if not selected_channel or len(selected_channel) > 1:
            QMessageBox.about(
                self,
                "Error",
                "Select one channel to show spectral analysis",
            )
            return

        channel = selected_channel[0]
        
        signal_data = self.midata.signals[channel][
            int(self.start_end[0]*self.midata.sf[channel]) : 
            int(self.start_end[1]*self.midata.sf[channel])
        ]
        
        freq, psd = spectrum(signal=signal_data,
                             sf=self.midata.sf[channel],
                             relative=False)
        
        f, t, Sxx = spectrogram(signal=signal_data,
                                sf=self.midata.sf[channel],
                                step=1, window=5, norm=True)

        bandPower = band_power(psd=psd, freq=freq, 
                               bands=[[0.5, 4, 'delta'], [4, 9, 'theta']])
        
        ratio = bandPower['delta'] / bandPower['theta']
        
        self.spec_window.show_(spectrum=[psd, freq], 
                               spectrogram=[f, t, Sxx],
                               percentile_=self.spectrogram_percentile,
                               ratio=ratio)
        
        self.spec_window.activateWindow()
        self.spec_window.setWindowState(
                self.spec_window.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.spec_window.showNormal()

    def set_show_duration(self, type_="Combo"):
        """Set show_duration with ShowRangeCombo or EpochNumSpin"""

        if type_ == "Combo":
            selected_idx = self.ShowRangeCombo.currentIndex()
            if (
                self.ShowRangeCombo_dict[selected_idx] + self.current_sec
                >= self.total_seconds
            ):
                self.show_duration = 30
                self.current_sec = 0
                self.ShowRangeCombo.setCurrentIndex(0)
            else:
                self.show_duration = self.ShowRangeCombo_dict[selected_idx]
        if type_ == "Spin":
            show_duration = self.EpochNumSpin.value() * self.epoch_length
            if show_duration + self.current_sec >= self.total_seconds:
                self.show_duration = 30
                self.current_sec = 0
                self.EpochNumSpin.setValue(6)
            else:
                self.show_duration = show_duration

        self.reset_sec_limit()
        self.redraw_all(second=self.current_sec)
        self.ScrollerBar.setPageStep(self.show_duration)

    def CustomSecondCheck_clicked(self):
        """If CustomSecondCheck was clicked"""
        if self.CustomSecondsCheck.isChecked():
            self.ShowRangeCombo.setDisabled(True)
            self.EpochNumSpin.setEnabled(True)
            self.set_show_duration(type_="Spin")
        else:
            self.ShowRangeCombo.setEnabled(True)
            self.EpochNumSpin.setDisabled(True)
            self.set_show_duration(type_="Combo")

    def ShowRangeCombo_changed(self):
        """Triggered by ShowRangeCombo index change"""
        self.set_show_duration(type_="Combo")

    def EpochNumSpin_changed(self):
        """Triggered by EpochNumSpin value change"""
        self.set_show_duration(type_="Spin")

    def nrem_label(self):
        """label start_end as nrem laebl, triggered by NREMBt"""
        self.append_sleep_state(sleep_type=1)

    def rem_label(self):
        """label start_end label as rem label, triggered by REMBt"""
        self.append_sleep_state(sleep_type=2)
    
    def wake_label(self):
        """label start_end label as wake label, triggered by WakeBt"""
        self.append_sleep_state(sleep_type=3)
    
    def init_label(self):
        """label start_end label as init label, triggered by InitBt"""
        self.append_sleep_state(sleep_type=4)

    def append_sleep_state(self, sleep_type=None):
        """Append sleep state to self.mianno.sleep_state"""
        if len(self.start_end) != 2:
            QMessageBox.about(self, "Info", 
                              "Please select a start end area in Sleep state mode")
            return
        
        if len(self.start_end) == 2:
            self.mianno.sleep_state[self.start_end[0]: self.start_end[1]] = \
                [sleep_type] * (self.start_end[1] - self.start_end[0])
        
        self.is_saved = False
        self.replot_sleep_state_bg(state=sleep_type)
        self.plot_hypo()

    def append_start_end(self):
        """Append start end label to self.mianno.start_end
        Triggered by self.AnnotateBt
        """

        if not self.StartEndRadio.isChecked():
            QMessageBox.about(self, "Info", "Use Start-End mode")
            return
        if len(self.start_end_ms) != 2:
            QMessageBox.about(self, "Info", "Please select a start end area")
            return
        
        self.label_dialog._type = 1
        self.label_dialog.show_contents()
        self.label_dialog.exec()
        if self.label_dialog.closed:
            return
        
        label_name = self.label_dialog.label_name

        # Add start_end label to self.mianno.start_end
        self.mianno.start_end.append(
            [self.start_end_ms[0], self.start_end_ms[1], label_name])

        self.plot_start_end_label_line()
    
        self.is_saved = False

    def about_bar_dispatcher(self, signal):
        """Triggered by AboutBar action, show About dialog"""
        if signal.text() == "About":
            self.about_dialog.exec()

    def load_bar_dispatcher(self, signal):
        """Triggered by LoadBar action, load data, load annotation, show"""
        if signal.text() == "Load Data":
            self.load_data()
        if signal.text() == "Load Annotation":
            self.load_anno()
        if signal.text() == "Show":
            self.check_show()

    def save_bar_dispatcher(self, signal):
        """Triggered by SaveBar action, save data, save annotation"""
        if signal.text() == "Save Data":
            self.save_data()
        if signal.text() == "Save Annotation":
            self.save_anno()

    def save_anno(self):
        """Save annotation into file"""
        save_thread = SaveThread(file=[self.mianno, self.midata], 
                                 file_path=self.anno_path)
        saved = save_thread.save_anno()
        if saved:
            self.is_saved = True
            QMessageBox.about(self, "Info", "Annotation saved")
        save_thread.quit()

    def save_config(self, config_dict):
        """Save config"""
        for key, value in config_dict.items():
            self.config.set('gui', key, value)
        save_thread = SaveThread(file=self.config, 
                                 file_path='./misleep/config.ini')
        save_thread.save_config()
        save_thread.quit()

    def closeEvent(self, event):
        """Check if saved and quit"""
        if not self.is_saved:
            box = QMessageBox.question(self, 'Warning',
                                       'Your labels haven\'t been saved, discard?\n'
                                       'Yes: Save and quit\nNo: Discard\nCancel: Back to sleep window',
                                       QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)

            if box == QMessageBox.Yes:
                self.save_anno()

                event.accept()
            elif box == QMessageBox.No:

                event.accept()
            else:
                event.ignore()