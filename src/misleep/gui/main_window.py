# -*- coding: UTF-8 -*-
"""Main window of the MiSleep GUI.

All plotting is based on the annotation: the signal area shows the raw
channels with sleep-state background colors, the spectrogram strip, the
hypnogram, and a collection of dock widgets for channel/scoring tools.
"""

import copy
import datetime
import json
import os

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtCore import QEvent, QTimer, Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView,
    QAbstractSpinBox,
    QApplication,
    QComboBox,
    QFileDialog,
    QGridLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from misleep.config import load_config, save_config, user_config_path
from misleep.data import MiAnnotation, MiData
from misleep.gui.config_dialog import SettingsDialog
from misleep.gui.dialogs import (
    AboutDialog,
    AutoStageCausalTransformerDialog,
    AutoStageLightGBMDialog,
    EventListDialog,
    HorizontalLineDialog,
    LabelDialog,
    SaveDataDialog,
    SpindleDetectionDialog,
    StateSpectralDialog,
    SWADetectionDialog,
    TransferResultDialog,
)
from misleep.gui.event_filters import WheelInputGuard
from misleep.gui.qt_utils import (
    ChannelListModel,
    CollapsibleSection,
    app_icon,
    create_new_mianno,
    identify_startend_color,
)
from misleep.gui.spec_window import SpecWindow
from misleep.gui.style import THEMES, apply_theme, retheme_figures
from misleep.gui.uis.main_window_ui import Ui_MiSleep
from misleep.gui.workers import SaveThread
from misleep.io.annotation import load_bio_anno, load_misleep_anno
from misleep.io.edf import load_edf
from misleep.io.mat import load_mat
from misleep.logger import logger
from misleep.preprocessing.spectral import band_power, spectrogram, spectrum
from misleep.utils.annotation import lst2group


class MainWindow(QMainWindow, Ui_MiSleep):
    """Main window of MiSleep."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Load configuration first so the GUI can honor the user's theme.
        self.config = load_config()

        # Apply the selected theme (light / dark): Qt style + fonts +
        # matplotlib defaults, so the plot area matches the chrome.
        self._theme_name = self.config.get("gui", "theme", fallback="light")
        if self._theme_name not in THEMES:
            self._theme_name = "light"
        app = QApplication.instance()
        if app is not None:
            apply_theme(app, self._theme_name)
        self._set_plot_colors()

        logger.info(f"Initializing MiSleep {self.config['gui']['version']}")

        self.midata = None
        self.mianno = None

        # Original data and label file paths
        self.data_path = ""
        self.anno_path = ""

        # Initial params
        self.current_sec = 0
        self.show_duration = 30  # Seconds of duration to plot
        self.total_seconds = 0  # Total seconds for plot
        self.y_lims = None  # list of y lim for each channel
        self.y_shift = None  # list of y shift for each channel
        self.show_idx = None  # Channels to show in the plot area
        self.state_map_dict = {int(key): value for key, value
                               in json.loads(self.config["gui"]["statemap"]).items()}
        self.state_color_dict = {int(key): value for key, value
                                 in json.loads(self.config["gui"]["statecolor"]).items()}
        self.start_end_color_dict = dict(json.loads(self.config["gui"]["startendcolor"].replace("'", '"')).items())

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

        # Signal area figure
        self.signal_figure = plt.figure()
        self.signal_ax = self.signal_figure.subplots()
        self.signal_figure.tight_layout(h_pad=0, w_pad=0)
        self.signal_figure.subplots_adjust(hspace=0)
        self.signal_canvas = FigureCanvas(self.signal_figure)
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
            self.current_sec, color="gray", alpha=0.8)

        # Caches for fast page flips (spectrogram / hypnogram are static
        # between flips, so they are computed once and reused).
        self._spec_full_cache = {}           # channel idx -> (f, t, Sxx) of whole file
        self._spec_cache_max_sec = 4 * 3600  # longer files compute per window
        self._hypo_key = None                # fingerprint of the drawn hypnogram base
        self._hypo_steps = []                # base step artists of the hypnogram
        self._hypo_transient = []            # per-flip overlay artists
        self._signal_artists = {}            # signal-axes idx -> artists we own
        self._spec_artist = None             # current spectrogram QuadMesh

        # Initial params for widgets
        self.channel_slm = ChannelListModel()

        # Initial dialogs and secondary windows
        self.about_dialog = AboutDialog(version=self.config["gui"]["version"],
                                        update_time=self.config["gui"]["updatetime"])
        self.spec_window = SpecWindow()
        self.label_dialog = LabelDialog(config=self.config)
        self.transfer_result_dialog = TransferResultDialog()
        self.state_spectral_dialog = StateSpectralDialog(config=self.config)
        self.save_data_dialog = SaveDataDialog()
        self.horizontal_line_dialog = HorizontalLineDialog()
        # The horizontal_line dict contains the line value, line color, line comment
        # example: {'ch1': [23.33, '#ff0000', '3 x Standard deviation', horizontalLineObject]}
        self.horizontal_line = {}
        self.axhline_horizontal = []

        self.swa_detection_dialog = SWADetectionDialog()
        self.spindel_detection_dialog = SpindleDetectionDialog()
        self.auto_stage_lightGBM_dialog = AutoStageLightGBMDialog()
        self.auto_stage_causalTransformer_dialog = AutoStageCausalTransformerDialog()

        # Check whether operations are saved or not
        self.is_saved = True

        # Timer to auto-save annotations every 5 minutes
        self.save_timer = QTimer()
        self.save_timer.timeout.connect(self.auto_save)

        # High-DPI / resolution: canvases track the scroll areas
        self.SignalArea.installEventFilter(self)
        self.HypnoArea.installEventFilter(self)
        self.signal_canvas.installEventFilter(self)
        self.hypo_canvas.installEventFilter(self)
        # The mouse wheel over the signal / hypnogram panels flips pages
        self.SignalArea.viewport().installEventFilter(self)
        self.HypnoArea.viewport().installEventFilter(self)

        # Unified right-hand sidebar (replaces the four separate docks)
        self._build_sidebar()
        self._thin_inputs()
        self.setMinimumSize(960, 600)
        self.setWindowIcon(app_icon())

        self.init_qt()

    # ------------------------------------------------------------------
    # Theme control
    # ------------------------------------------------------------------
    def _set_plot_colors(self):
        """Cache the theme colors used by the matplotlib canvases."""
        theme = THEMES[self._theme_name]
        self._plot_trace = theme["plot"]["trace"]
        self._plot_grid = theme["plot"]["grid"]

    def _update_theme_action(self):
        """Keep the menu-bar theme action text in sync with the theme."""
        if getattr(self, "theme_action", None) is not None:
            self.theme_action.setText(
                "Switch to Light Theme" if self._theme_name == "dark"
                else "Switch to Dark Theme")

    def toggle_theme(self):
        """Toggle between the light and dark themes and redraw everything."""
        self._theme_name = "dark" if self._theme_name == "light" else "light"
        app = QApplication.instance()
        if app is not None:
            apply_theme(app, self._theme_name)
        retheme_figures(self._theme_name)
        self._set_plot_colors()
        self._update_theme_action()
        # Persist the choice so the next launch keeps it
        self.save_config({"theme": self._theme_name})

        if self.midata is not None and self.mianno is not None:
            self.redraw_all(second=self.current_sec)
        else:
            self.clear_refresh(clf=True)
        logger.info("Theme switched to %s", THEMES[self._theme_name]["name"])

    def _build_sidebar(self):
        """Replace the four right docks with one tidy, fixed sidebar.

        The dock contents are re-parented into collapsible sections
        (Data / Channels / Scoring / Display) stacked in a single panel,
        so the right side always looks clean regardless of window size.
        """
        self._sections = []
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        vbox = QVBoxLayout(sidebar)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(8)

        def add_section(title, content, collapsed=False, stretch=0):
            sec = CollapsibleSection(title, content, collapsed=collapsed)
            vbox.addWidget(sec, stretch)
            self._sections.append(sec)
            return sec

        add_section("Data", self.MetaDock.widget(), collapsed=True)
        add_section("Channels", self.ChannelDock.widget(), stretch=1)
        add_section("Scoring", self.AnnotationDock.widget())
        add_section("Display", self.TimeDock.widget())

        # The sidebar lives in a scroll area (never clips on small screens)
        # and keeps a fixed, comfortable width next to the plot area.
        self.sidebar = sidebar
        scroll = QScrollArea()
        scroll.setObjectName("SidebarScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setWidget(sidebar)
        scroll.setFixedWidth(318)
        scroll.setMinimumHeight(120)
        self.sidebar_scroll = scroll
        self.gridLayout_3.addWidget(scroll, 0, 1, 3, 1)
        self.gridLayout_3.setColumnStretch(0, 1)
        self.gridLayout_3.setColumnStretch(1, 0)

        # The old docks are hidden - their widgets now live in the sidebar.
        for dock in (self.MetaDock, self.ChannelDock,
                     self.AnnotationDock, self.TimeDock):
            self.removeDockWidget(dock)
            dock.hide()

    def _thin_inputs(self):
        """Make spin boxes / combos in the docks narrower."""
        for name in ("FilterLowSpin", "FilterHighSpin", "PercentileSpin",
                     "SecondSpin", "SecondNumSpin"):
            spin = getattr(self, name, None)
            if spin is not None:
                spin.setFixedWidth(64)
        for name in ("FilterTypeCombo", "ShowRangeCombo"):
            combo = getattr(self, name, None)
            if combo is not None:
                combo.setFixedWidth(100)

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------
    def init_qt(self):
        """Wire up all Qt widget signals."""
        # MenuBar triggers
        self.actionAbout.triggered.connect(self.about_dialog.exec)
        self.actionConfig.triggered.connect(self.open_settings_dialog)
        self.actionLoadData.triggered.connect(self.load_data)
        self.actionLoadAnnotation.triggered.connect(self.load_anno)
        self.actionStateSpectral.triggered.connect(self.state_spectral)
        self.actionTransferResult.triggered.connect(self.transfer_result)
        self.actionAddLine.triggered.connect(self.add_horizontal_line)
        self.actionSWA_detection.triggered.connect(self.swa_detection)
        self.actionSpindle_Detection.triggered.connect(self.spindle_detection)
        self.actionLightGBM.triggered.connect(self.auto_stage_LightGBM)
        self.actionCausalTransformer.triggered.connect(self.auto_stage_CausalTransformer)
        self.actionSaveData.triggered.connect(self.save_data)

        # Spectrogram percentile
        self.PercentileSpin.setValue(self.spectrogram_percentile)
        self.PercentileSpin.setRange(0, 100)
        self.PercentileSpin.valueChanged.connect(self.spec_percentile_change)
        # Default spectrogram channel
        self.DefaultCh4SpecBt.clicked.connect(self.default_ch4Spec)

        # Scroll bar
        self.ScrollerBar.valueChanged.connect(self.scroller_change)
        self.ScrollerBar.setSingleStep(self.epoch_length)
        self.ScrollerBar.setPageStep(self.show_duration)

        # Time edits
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
        self.channel_slm.dataChanged.connect(self.channel_rename)
        # Channel order is changed with the Up/Down buttons (declared in the
        # .ui); editing only starts on double-click.
        self.ChListView.setEditTriggers(
            QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        self.channel_slm.rowsMoved.connect(self._on_channel_list_changed)
        self.channel_slm.rowsInserted.connect(self._on_channel_list_changed)
        self.channel_slm.rowsRemoved.connect(self._on_channel_list_changed)
        self._updating_ch_list = False
        # Channel move arrows (declared in the .ui beside the percentile box)
        self.MoveUpBt.clicked.connect(lambda: self.move_channel("up"))
        self.MoveDownBt.clicked.connect(lambda: self.move_channel("down"))

        # Filter
        self.FilterTypeCombo.currentIndexChanged.connect(self.FilterTypeCombo_change)
        self.FilterConfirmBt.clicked.connect(self.filter_confirm)

        # Spectrum window
        self.PlotSpecBt.clicked.connect(self.show_spec_window)

        # Custom second spin edit and ShowRangeCombo
        self.ShowRangeCombo.setEnabled(True)
        self.SecondNumSpin.setDisabled(True)
        self.SecondNumSpin.setRange(5, 3600)
        self.SecondNumSpin.setValue(30)
        self.SecondNumSpin.valueChanged.connect(self.SecondNumSpin_changed)
        self.ShowRangeCombo.currentIndexChanged.connect(self.ShowRangeCombo_changed)
        self.CustomSecondsCheck.clicked.connect(self.CustomSecondCheck_clicked)

        # Label radio: start_end by default
        self.SleepStateRadio.setChecked(True)
        self.SleepStateRadio.toggled.connect(lambda: self.radio_recheck(self.SleepStateRadio))
        self.StartEndRadio.toggled.connect(lambda: self.radio_recheck(self.StartEndRadio))

        # Label buttons
        self.NREMBt.clicked.connect(self.nrem_label)
        self.REMBt.clicked.connect(self.rem_label)
        self.WakeBt.clicked.connect(self.wake_label)
        self.InitBt.clicked.connect(self.init_label)
        self.LabelBt.clicked.connect(self.append_start_end)

        # Shortcuts
        self.labelSc = QShortcut(QKeySequence("a"), self)
        self.labelSc.activated.connect(self.append_start_end)
        self.specSc = QShortcut(QKeySequence("s"), self)
        self.specSc.activated.connect(self.show_spec_window)

        self.next_pageSc = QShortcut(QKeySequence("Right"), self)
        self.next_pageSc.activated.connect(self.next_page)
        self.previous_pageSc = QShortcut(QKeySequence("Left"), self)
        self.previous_pageSc.activated.connect(self.previous_page)
        self.next_epochSc = QShortcut(QKeySequence("Down"), self)
        self.next_epochSc.activated.connect(self.next_epoch)
        self.previous_epochSc = QShortcut(QKeySequence("Up"), self)
        self.previous_epochSc.activated.connect(self.previous_epoch)

        # NOTE: page-flipping with the mouse wheel is handled only by the
        # event filter on the signal / hypnogram areas (see eventFilter),
        # so scrolling over docks/tools never moves the signal window.

        # Load data and annotation shortcuts
        self.load_dataSc = QShortcut(QKeySequence("Shift+D"), self)
        self.load_dataSc.activated.connect(self.load_data)
        self.load_annoSc = QShortcut(QKeySequence("Shift+A"), self)
        self.load_annoSc.activated.connect(self.load_anno)

        # Save labels
        self.SaveLabelBt.clicked.connect(self.save_anno)
        self.saveSc = QShortcut(QKeySequence("Ctrl+S"), self)
        self.saveSc.activated.connect(self.save_anno)

        # Dynamic state-label buttons in the Annotation dock
        self._sync_state_buttons()

        # Scalar input
        self.MultipleScalerConfirmBt.clicked.connect(self.multiple_scaler)

        self.change_Bts_status(True)
        self._build_menus()
        # Marker / start-end event list viewers (declared in the .ui beside Save)
        self.MarkerListBt.clicked.connect(self.show_marker_list)
        self.StartEndListBt.clicked.connect(self.show_start_end_list)
        logger.info("MiSleep ready - open a data file to start")

        # Wheel over spin boxes / combos must not change their values
        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(WheelInputGuard(app))

    def change_Bts_status(self, status=True):
        """Enable/disable buttons according to whether data is loaded."""
        meta_content = self.MetaDock.widget()
        if meta_content is not None:
            meta_content.setDisabled(status)
        self.AcTimeEdit.setDisabled(status)
        self.DeleteChBt.setDisabled(status)
        self.HideChBt.setDisabled(status)
        self.ScalerDownBt.setDisabled(status)
        self.ShiftDownBt.setDisabled(status)
        self.ShowChBt.setDisabled(status)
        self.ScalerUpBt.setDisabled(status)
        self.ShiftUpBt.setDisabled(status)
        self.FilterConfirmBt.setDisabled(status)
        self.DefaultCh4SpecBt.setDisabled(status)
        self.FilterTypeCombo.setDisabled(status)
        self.PlotSpecBt.setDisabled(status)
        self.LabelBt.setDisabled(status)
        self.StartEndRadio.setDisabled(status)
        self.SleepStateRadio.setDisabled(status)
        self.SaveLabelBt.setDisabled(status)
        self.MarkerRadio.setDisabled(status)
        self.MarkerListBt.setDisabled(status)
        self.StartEndListBt.setDisabled(status)
        self.MoveUpBt.setDisabled(status)
        self.MoveDownBt.setDisabled(status)
        for bt in getattr(self, "_state_btns", {}).values():
            bt.setDisabled(status)
        self.DateTimeEdit.setDisabled(status)
        self.ShowRangeCombo.setDisabled(status)
        self.SecondSpin.setDisabled(status)
        self.labelSc.setEnabled(not status)
        self.specSc.setEnabled(not status)
        self.next_pageSc.setEnabled(not status)
        self.previous_pageSc.setEnabled(not status)
        self.next_epochSc.setEnabled(not status)
        self.previous_epochSc.setEnabled(not status)
        self.multipleScalerEditor.setDisabled(status)
        self.MultipleScalerConfirmBt.setDisabled(status)

        self.menuTools.setDisabled(status)
        self.menuResult.setDisabled(status)

    def _build_menus(self):
        """Polish the menu bar: File extras, Settings rename, View dock menu."""
        # File: add "Save Annotation" and "Exit"
        save_anno_action = self.menuFile.addAction(app_icon(), "Save Annotation", self.save_anno)
        save_anno_action.setShortcut(QKeySequence("Ctrl+S"))
        self.menuFile.insertAction(self.actionSaveData, save_anno_action)
        self.menuFile.addSeparator()
        self.menuFile.addAction("Exit", self.close)

        # Help: Settings lives on its own top-level menu, not in About
        self.menuHelp.removeAction(self.actionConfig)

        # A dedicated Settings menu on the menu bar
        settings_menu = self.menuBar.addMenu("Settings")
        settings_action = settings_menu.addAction(
            app_icon(), "Settings…", self.open_settings_dialog)
        settings_action.setToolTip("Open the in-application settings dialog")
        settings_menu.addSeparator()
        self.theme_action = settings_menu.addAction(
            "Switch to Dark Theme", self.toggle_theme)
        self.theme_action.setShortcut(QKeySequence("Ctrl+Shift+T"))
        self._update_theme_action()

        # View: sidebar section visibility toggles (mirrors the headers)
        view_menu = self.menuBar.addMenu("&View")
        for sec in self._sections:
            action = view_menu.addAction(sec.title)
            action.setCheckable(True)
            action.setChecked(sec.is_expanded())
            action.toggled.connect(sec.set_expanded)
            sec.header.toggled.connect(action.setChecked)

    # ------------------------------------------------------------------
    # Data / annotation loading
    # ------------------------------------------------------------------
    def load_data(self):
        """Triggered by actionLoadData: ask for a signal file and open it."""
        data_path, _ = QFileDialog.getOpenFileName(
            self, "Select data file",
            f"{self.config['gui']['openpath']}",
            ".*(*.mat *.MAT *.edf *.EDF);;Matlab Files (*.mat *.MAT);;EDF Files (*.edf *.EDF)")

        if data_path == "":
            return
        self.open_data(data_path)

    def open_data(self, data_path):
        """Load a signal file (no file dialog) and show it.

        Used both by the GUI's file dialog and when MiSleep is launched
        with a data file argument (``misleep data.mat``) or by
        double-clicking a registered file.

        Parameters
        ----------
        data_path : str
            Path of the ``.mat`` or ``.edf`` file to load.
        """
        if not os.path.exists(data_path):
            QMessageBox.about(
                self, "Error",
                f"Data file not found:\n{data_path}")
            return

        self.data_path = data_path
        if self.data_path.endswith((".mat", ".MAT")):
            self.midata = load_mat(data_path=self.data_path)
            if self.midata is None:
                QMessageBox.about(
                    self, "Error",
                    r"Data file invalid, check "
                    r"<a href='https://github.com/BryanWang0702/MiSleep'>MiSleep</a> for detail.")
                self.data_path = ""
                self.change_Bts_status(True)
                self.mianno = None
                return

        if self.data_path.endswith((".edf", ".EDF")):
            try:
                self.midata = load_edf(data_path=self.data_path)
            except Exception:
                QMessageBox.about(
                    self, "Error",
                    r"Data file invalid, check "
                    r"<a href='https://github.com/BryanWang0702/MiSleep'>MiSleep</a> for detail.")
                self.data_path = ""
                self.change_Bts_status(True)
                self.mianno = None
                return

        if self.midata is None:
            QMessageBox.about(
                self, "Error",
                f"Unsupported file type: {self.data_path}")
            self.data_path = ""
            return

        # Save config
        self.save_config({"openpath": self.data_path})

        # New file: drop the cached whole-file spectrograms
        self._spec_full_cache = {}

        # Set meta info
        self.DataPathEdit.setText(self.data_path)
        self.ac_time = datetime.datetime.strptime(self.midata.time, "%Y%m%d-%H:%M:%S")
        self.AcTimeEdit.setDateTime(self.ac_time)

        # Set channel infos
        self.fill_channel_listView()

        self.start_end = []
        self.current_spectrogram_idx = 0
        self.mianno = None
        self.anno_path = ""
        self.AnnoPathEdit.setText("")

        self.clear_refresh(clf=True)

        try:
            self.check_show()
        except Exception as e:
            logger.error(f"Check Show ERROR: {e}")

    def load_anno(self):
        """Triggered by actionLoadAnnotation: ask for an annotation file."""
        anno_path, _ = QFileDialog.getOpenFileName(
            self, "Select annotation file",
            f"{self.config['gui']['openpath']}",
            "txt Files (*.txt *.TXT)")

        if anno_path == "":
            return
        self.open_annotation(anno_path)

    def open_annotation(self, anno_path):
        """Load an annotation file (no file dialog).

        Used both by the GUI's file dialog and when MiSleep is launched
        with an annotation argument (``misleep data.mat anno.txt``).

        Parameters
        ----------
        anno_path : str
            Path of the annotation ``.txt`` file.
        """
        if not os.path.exists(anno_path):
            QMessageBox.about(self, "Error", f"Annotation file not found:\n{anno_path}")
            return

        self.anno_path = anno_path
        _mianno = self.mianno

        if self.anno_path.endswith((".txt", ".TXT")):
            try:
                with open(self.anno_path, "r", encoding="utf-8", errors="ignore") as f:
                    file = f.read()
                if file[:5] == "Start":
                    self.mianno = load_bio_anno(self.anno_path)
                else:
                    self.mianno = load_misleep_anno(self.anno_path, state_map=self.state_map_dict)
            except AssertionError as e:
                if e.args[0] == "Empty":
                    if isinstance(self.midata, MiData):
                        self.mianno = create_new_mianno(self.midata.duration)
                    else:
                        QMessageBox.about(
                            self, "Error",
                            "To create a new annotation file, load a data file first.")
                        self.anno_path = ""
                        self.change_Bts_status(True)
                        self.mianno = None
                        return

                if e.args[0] == "Invalid":
                    QMessageBox.about(
                        self, "Error",
                        r"Annotation file invalid, check "
                        r"<a href='https://github.com/BryanWang0702/MiSleep'>MiSleep</a> for detail.")
                    self.anno_path = ""
                    self.change_Bts_status(True)
                    self.mianno = None
                    return

        # Save config
        self.save_config({"openpath": self.anno_path})

        # Set meta info
        self.AnnoPathEdit.setText(self.anno_path)

        self.clear_refresh(clf=True)

        try:
            self.check_show(_mianno)
        except Exception as e:
            logger.error(f"Check Show ERROR: {e}")

    def check_show(self, mianno=None):
        """Validate data/annotation and draw everything.

        Parameters
        ----------
        mianno : MiAnnotation, optional
            Keep the previous annotation when loading a new one failed.
        """
        if not isinstance(self.midata, MiData):
            QMessageBox.about(self, "Error", "Load data file first.")
            self.midata = None
            self.mianno = None
            return

        if isinstance(self.midata, MiData) and not isinstance(self.mianno, MiAnnotation):
            self.mianno = create_new_mianno(self.midata.duration)

        self.show_idx = list(range(self.midata.n_channels))
        self.y_lims = [max(abs(each[:1000])) for each in self.midata.signals]
        self.y_lims = [1e-3 if each == 0.0 else each for each in self.y_lims]
        self.y_shift = [0 for _ in range(self.midata.n_channels)]

        if abs(self.midata.duration - self.mianno.anno_length) >= 600:
            QMessageBox.about(self, "Error", "Data and annotation do not match!")
            self.anno_path = ""
            self.AnnoPathEdit.setText(self.anno_path)
            if mianno:
                self.mianno = mianno
            if not isinstance(self.mianno, MiAnnotation):
                self.mianno = create_new_mianno(self.midata.duration)
        self.total_seconds = self.midata.duration if \
            self.midata.duration < self.mianno.anno_length else self.mianno.anno_length
        self.reset_sec_limit()

        self.hypo_ax = self.hypo_figure.subplots(nrows=1, ncols=1)
        # new axes: the cached hypnogram base must be rebuilt
        self._hypo_key = None
        self._hypo_steps = []
        self._hypo_transient = []

        # Set canvases for the plot areas
        self.SignalArea.setWidget(self.signal_canvas)
        self.HypnoArea.setWidget(self.hypo_canvas)

        self.horizontal_line = {}
        for channel in self.midata.channels:
            self.horizontal_line[channel] = []

        self.redraw_all(second=0)
        self.clear_refresh(clf=False)
        self.change_Bts_status(False)

        self.setWindowTitle(
            f"MiSleep - {os.path.basename(self.data_path)} - {os.path.basename(self.anno_path)}")
        self.start_end = []
        self.mianno._state_map = self.state_map_dict

        logger.info(f"Load SUCCEED: data - {self.data_path}, anno - {self.anno_path}")

        # Load feedback
        logger.info(
            "Loaded: %s - %d channel(s), %d s",
            os.path.basename(self.data_path),
            self.midata.n_channels, self.total_seconds)

        # Start the auto-save timer (5 min)
        self.save_timer.start(60 * 5 * 1000)

        # Fit the canvases to the (high-DPI aware) window size
        self._fit_canvases()

    def reset_sec_limit(self):
        """Update scrollbar / spin / datetime limits when show duration changes."""
        self.ScrollerBar.setRange(0, self.total_seconds - self.show_duration)
        self.SecondSpin.setRange(0, self.total_seconds - self.show_duration)

        self.DateTimeEdit.blockSignals(True)
        self.DateTimeEdit.setDateTimeRange(
            self.ac_time,
            self.ac_time + datetime.timedelta(seconds=self.total_seconds - self.show_duration))
        self.DateTimeEdit.blockSignals(False)

    # ------------------------------------------------------------------
    # Plotting
    # ------------------------------------------------------------------
    def clear_refresh(self, clf=False):
        """Clear and refresh all plot canvases."""
        if clf:
            self.signal_figure.clf()
            self.hypo_figure.clf()
            # the old axes are gone; force a rebuild on the next plot
            self.signal_ax = None
            self._signal_artists = {}
            self._spec_artist = None
            self._hypo_key = None
            self._hypo_steps = []
            self._hypo_transient = []

        self.hypo_figure.canvas.draw()
        self.hypo_figure.canvas.flush_events()
        self.signal_figure.canvas.draw()
        self.signal_figure.canvas.flush_events()

    def _fit_canvases(self):
        """Resize the matplotlib figures to match their widgets.

        The widget size is converted to **device pixels** (multiplied by
        ``devicePixelRatio``) before being fed to ``set_size_inches``, so
        the figure fills the widget exactly on high-DPI / scaled displays
        (e.g. 2K at 125-150 %). A modest minimum keeps scrollbars instead
        of a crushed plot.
        """
        try:
            sig_dpr = self.signal_canvas.devicePixelRatioF() or 1.0
            sig_w = self.signal_canvas.width() * sig_dpr
            sig_h = self.signal_canvas.height() * sig_dpr
            if sig_w < 50 or sig_h < 50:
                sig_w = self.SignalArea.viewport().width() * sig_dpr
                sig_h = self.SignalArea.viewport().height() * sig_dpr
            if sig_w > 50 and sig_h > 50:
                self.signal_figure.set_size_inches(
                    sig_w / self.signal_figure.dpi,
                    sig_h / self.signal_figure.dpi)
                self.signal_canvas.setMinimumSize(300, 200)
                self._apply_signal_layout()
                self.signal_figure.canvas.draw_idle()

            hypo_dpr = self.hypo_canvas.devicePixelRatioF() or 1.0
            hypo_w = self.hypo_canvas.width() * hypo_dpr
            hypo_h = self.hypo_canvas.height() * hypo_dpr
            if hypo_w < 50 or hypo_h < 50:
                hypo_w = self.HypnoArea.viewport().width() * hypo_dpr
                hypo_h = self.HypnoArea.viewport().height() * hypo_dpr
            if hypo_w > 50 and hypo_h > 50:
                self.hypo_figure.set_size_inches(
                    hypo_w / self.hypo_figure.dpi,
                    max(1.0, hypo_h / self.hypo_figure.dpi))
                self.hypo_canvas.setMinimumSize(300, 60)
                self.hypo_figure.canvas.draw_idle()
        except Exception as e:  # pragma: no cover
            logger.debug(f"fit canvases skipped: {e}")

    def eventFilter(self, obj, event):
        """Track canvas/scroll-area resizes; flip pages on mouse wheel."""
        if event.type() == QEvent.Type.Resize:
            if obj in (self.signal_canvas, self.hypo_canvas,
                       self.SignalArea, self.HypnoArea):
                self._fit_canvases()
        elif event.type() == QEvent.Type.Wheel:
            if obj in (self.SignalArea.viewport(), self.HypnoArea.viewport(),
                       self.signal_canvas, self.hypo_canvas):
                delta = event.angleDelta().y()
                if delta < 0:
                    self.next_page()
                elif delta > 0:
                    self.previous_page()
                return True
        return super().eventFilter(obj, event)

    def resizeEvent(self, event):
        """Keep the matplotlib canvases in sync with the window size."""
        super().resizeEvent(event)
        self._fit_canvases()

    def showEvent(self, event):
        """Fit the canvases once the window is actually shown."""
        super().showEvent(event)
        QTimer.singleShot(0, self._fit_canvases)

    def _choose_tick_step(self, duration):
        """Pick a tick interval (seconds) so ~6-24 x ticks are shown."""
        for s in (5, 10, 15, 30, 60, 120, 300, 600, 900, 1800, 3600):
            if duration / s <= 24:
                return s
        return 3600

    def plot_signals(self, flush=True, clf=True, replot_axes=None):
        """Plot the signal area: spectrogram strip + one box per channel.

        Every channel gets its own axes (box) with its own y scale, so
        the boxes are independent. The figure fills the whole signal
        widget (see :meth:`_fit_canvases`).

        Parameters
        ----------
        flush : bool
            Whether to redraw the canvas.
        clf, replot_axes : kept for API compatibility (always full redraw).
        """
        n = len(self.show_idx)
        need = n + 1  # spectrogram strip + one box per channel
        # Reuse the existing axes when the channel count is unchanged - much
        # faster than recreating them on every page flip.
        current = getattr(self, "signal_ax", None)
        if current is None or not isinstance(current, (list, tuple)) \
                or len(current) != need:
            self.signal_figure.clf()
            self.signal_ax = list(self.signal_figure.subplots(
                nrows=need, ncols=1,
                gridspec_kw={"height_ratios": [0.8] + [1.0] * n}))
            self._signal_artists = {}
            self._spec_artist = None
        else:
            # Remove only the artists we own from the previous flip - far
            # cheaper than clearing the whole axes.
            for ax_idx, artists in self._signal_artists.items():
                for art in artists:
                    try:
                        art.remove()
                    except Exception:
                        pass
            self._signal_artists = {}
        self.plot_spectrogram()

        # Sleep-state groups inside the current window
        sleep_state = self.mianno.sleep_state[
            self.current_sec: self.current_sec + self.show_duration + 1]
        sleep_state = lst2group([i, each] for i, each in enumerate(sleep_state))

        tick_step = self._choose_tick_step(self.show_duration)

        for i, each in enumerate(self.show_idx):
            ax = self.signal_ax[i + 1]
            y_lim = self.y_lims[each]
            y_shift = self.y_shift[each]
            sf = self.midata.sf[each]

            seg = self.midata.signals[each][
                int(self.current_sec * sf): int(
                    (self.current_sec + self.show_duration) * sf)]
            # Downsample dense traces for fast drawing (8k points is far
            # beyond screen resolution yet keeps page flips snappy)
            max_points = 8000
            step = max(1, -(-len(seg) // max_points))  # ceil division
            if step > 1:
                line, = ax.plot(np.arange(0, len(seg), step), seg[::step],
                                color=self._plot_trace, linewidth=0.5)
            else:
                line, = ax.plot(seg, color=self._plot_trace, linewidth=0.5)
            self._signal_artists.setdefault(i + 1, []).append(line)
            ax.set_ylim(ymin=-y_lim + y_shift, ymax=y_lim + y_shift)
            ax.set_xlim(xmin=0, xmax=self.show_duration * sf)
            ax.xaxis.set_ticks([])
            ax.yaxis.set_ticks([])
            ax.set_ylabel(f"{self.midata.channels[each]}\n{y_lim:.2e}")

            # grid lines: 5 s for short windows, tick step for long ones
            grid_step = 5 if self.show_duration < 300 else tick_step
            for pos_ in range(0, self.show_duration, grid_step):
                grid_line = ax.axvline(pos_ * sf, color=self._plot_grid,
                                       linestyle="--", linewidth=1, alpha=0.45)
                self._signal_artists[i + 1].append(grid_line)

            # Sleep-state background: one rectangle per run (the fill spans
            # the full height, so two x-points are exact and cheap to draw)
            for state in sleep_state:
                fill = ax.fill_between(
                    [int(state[0] * sf), int(state[1] * sf)],
                    -y_lim + y_shift, y_lim + y_shift,
                    facecolor=self.state_color_dict[state[2]],
                    alpha=float(self.config["gui"]["statecolorbgalpha"]))
                self._signal_artists[i + 1].append(fill)

        # Time ticks only on the last channel box (auto-reduced for long windows)
        last_sf = self.midata.sf[self.show_idx[-1]]
        self.signal_ax[-1].xaxis.set_ticks(
            [int(each * last_sf) for each in range(0, self.show_duration + 1, tick_step)],
            range(self.current_sec, self.current_sec + self.show_duration + 1, tick_step),
            rotation=45)
        if self.show_duration < 300:
            self.signal_ax[-1].xaxis.set_ticks(
                [int(each * last_sf) for each in range(0, self.show_duration + 1)],
                minor=True)

        if self.StartEndRadio.isChecked():
            self.plot_start_end_line(flush=False, ms=True)
        if self.SleepStateRadio.isChecked():
            self.plot_start_end_line(flush=False)
        self.plot_marker_line(flush=False)
        self.plot_start_end_label_line(flush=False)
        self.plot_horizontal_line(flush=False)

        # Keep the panels tightly packed (no gaps between boxes); the full
        # tight_layout runs on resize only (see _fit_canvases), not on every
        # page flip - that alone shaves ~20 ms off each flip.
        self.signal_figure.subplots_adjust(hspace=0)

        if flush:
            self.signal_figure.canvas.draw()
            self.signal_figure.canvas.flush_events()

    def _apply_signal_layout(self):
        """Tighten the signal figure layout so the panels touch each other."""
        try:
            self.signal_figure.tight_layout(h_pad=0, w_pad=0)
            self.signal_figure.subplots_adjust(hspace=0)
        except Exception as e:  # pragma: no cover
            logger.debug(f"signal layout skipped: {e}")

    def replot_sleep_state_bg(self, state):
        """Replot the sleep-state background of the selected start-end area."""
        replot_start = 0 if self.current_sec >= self.start_end[0] \
            else (self.start_end[0] - self.current_sec)
        replot_end = self.show_duration if (
            self.current_sec + self.show_duration <= self.start_end[1]
        ) else (self.start_end[1] - self.current_sec)

        for i, each in enumerate(self.show_idx):
            y_lim = self.y_lims[each]
            y_shift = self.y_shift[each]
            sf = self.midata.sf[each]
            x = range(int(replot_start * sf), int(replot_end * sf))
            cover = self.signal_ax[i + 1].fill_between(
                x, -y_lim + y_shift, y_lim + y_shift,
                facecolor=THEMES[self._theme_name]["plot"]["bg"], alpha=1)
            fill = self.signal_ax[i + 1].fill_between(
                x, -y_lim + y_shift, y_lim + y_shift,
                facecolor=self.state_color_dict[state],
                alpha=float(self.config["gui"]["statecolorbgalpha"]))
            self._signal_artists.setdefault(i + 1, []).extend([cover, fill])
        self.signal_figure.canvas.draw()
        self.signal_figure.canvas.flush_events()

    def spec_percentile_change(self):
        """Triggered by the spectrogram percentile spin box."""
        self.spectrogram_percentile = self.PercentileSpin.value()
        self.plot_spectrogram(flush=True)

    def default_ch4Spec(self):
        """Set the selected channel as the default spectrogram channel."""
        selected_channel = [each.row() for each in self.ChListView.selectedIndexes()]
        if len(selected_channel) != 1:
            QMessageBox.about(
                self, "Error",
                "Select one channel to be the default channel for spectrogram.")
            return
        self.current_spectrogram_idx = selected_channel[0]
        self.plot_spectrogram(flush=True)

    def plot_spectrogram(self, flush=False):
        """Redraw the spectrogram strip (cached whole-file STFT when possible)."""
        if self.midata is None:
            return
        # remove the previous spectrogram artist (cheaper than clearing axes)
        if getattr(self, "_spec_artist", None) is not None:
            try:
                self._spec_artist.remove()
            except Exception:
                pass
            self._spec_artist = None
        freq_range = [float(x) for x in self.config["gui"]["freq_range"].strip("[]").split(",")]
        ch = self.current_spectrogram_idx
        sf = self.midata.sf[ch]

        # Cache the STFT of the whole file per channel; page flips then only
        # slice the cached spectrogram instead of recomputing it.
        if ch not in self._spec_full_cache:
            if self.midata.duration <= self._spec_cache_max_sec:
                f, t, Sxx = spectrogram(
                    signal=self.midata.signals[ch], sf=sf,
                    band=freq_range, step=1, win_sec=5, norm=True)
                self._spec_full_cache[ch] = (f, t, Sxx)
            else:
                self._spec_full_cache[ch] = None  # too long: per-window

        cached = self._spec_full_cache.get(ch)
        if cached is not None:
            f, t, Sxx = cached
            sel = (t >= self.current_sec) & (t <= self.current_sec + self.show_duration)
            t = t[sel]
            Sxx = Sxx[:, sel]
        else:
            f, t, Sxx = spectrogram(
                signal=self.midata.signals[ch][
                    int(self.current_sec * sf): int(
                        (self.current_sec + self.show_duration) * sf)],
                sf=sf, band=freq_range, step=1, win_sec=5, norm=True)

        cmap_name = self.config.get("gui", "spectrogram_cmap", fallback="turbo")
        try:
            cmap = plt.get_cmap(cmap_name)
        except ValueError:
            cmap = plt.get_cmap("turbo")

        self.signal_ax[0].set_xticks([])
        self.signal_ax[0].set_ylim(freq_range)
        self.signal_ax[0].set_ylabel(f"{self.midata.channels[ch]}")
        self._spec_artist = self.signal_ax[0].pcolormesh(
            t, f, Sxx, cmap=cmap, vmax=np.percentile(Sxx, self.spectrogram_percentile))

        if flush:
            self.signal_figure.canvas.draw()
            self.signal_figure.canvas.flush_events()

    def plot_start_end_line(self, flush=True, ms=False):
        """Plot the interactive start/end selection lines in the signal area."""
        start_end = self.start_end_ms if ms else self.start_end
        for axvline in self.signal_start_end_axvline:
            try:
                axvline.remove()
            except Exception:
                pass
        self.signal_start_end_axvline = []
        for i, each in enumerate(start_end):
            if self.current_sec <= each <= self.current_sec + self.show_duration:
                for idx, show_ in enumerate(self.show_idx):
                    y_lim = self.y_lims[show_]
                    y_shift = self.y_shift[show_]
                    sf = self.midata.sf[show_]
                    if ms:
                        x = round((each - self.current_sec) * sf, 3)
                    else:
                        x = int((each - self.current_sec) * sf)

                    if i in (0, 1):
                        self.signal_start_end_axvline.append(
                            self.signal_ax[idx + 1].axvline(x, color="lime", alpha=1))

                if i == 0:
                    self.signal_start_end_axvline.append(
                        self.signal_ax[idx + 1].text(
                            x=x, y=-y_lim + y_shift, s="S", color="lime"))
                if i == 1:
                    self.signal_start_end_axvline.append(
                        self.signal_ax[idx + 1].text(
                            x=x, y=-y_lim + y_shift,
                            horizontalalignment="right", s="E", color="lime"))

        if flush:
            self.signal_figure.canvas.draw()
            self.signal_figure.canvas.flush_events()
            self.plot_hypo()

    def plot_marker_line(self, flush=True):
        """Plot marker lines in the signal area."""
        for axvline in self.signal_marker_axvline:
            try:
                axvline.remove()
            except Exception:
                pass
        self.signal_marker_axvline = []
        for each in self.mianno.marker:
            if self.current_sec <= each[0] <= self.current_sec + self.show_duration:
                for idx, show_ in enumerate(self.show_idx):
                    self.signal_marker_axvline.append(
                        self.signal_ax[idx + 1].axvline(
                            int((each[0] - self.current_sec) * self.midata.sf[show_]),
                            color="Red", alpha=1))
                self.signal_marker_axvline.append(
                    self.signal_ax[1].text(
                        x=int((each[0] - self.current_sec) * self.midata.sf[self.show_idx[0]]),
                        y=self.y_lims[self.show_idx[0]] + self.y_shift[self.show_idx[0]],
                        s=each[1], verticalalignment="top", color="Red"))

        if flush:
            self.signal_figure.canvas.draw()
            self.signal_figure.canvas.flush_events()
            self.plot_hypo()

    def plot_start_end_label_line(self, flush=True):
        """Plot the start/end annotation label lines."""
        for art in getattr(self, "signal_se_label_axvline", []):
            try:
                art.remove()
            except Exception:
                pass
        self.signal_se_label_axvline = []
        for each in self.mianno.start_end:
            if self.current_sec <= each[0] <= self.current_sec + self.show_duration:
                for idx, show_ in enumerate(self.show_idx):
                    self.signal_se_label_axvline.append(
                        self.signal_ax[idx + 1].axvline(
                            int((each[0] - self.current_sec) * self.midata.sf[show_]),
                            color=identify_startend_color(self.start_end_color_dict, each[2]),
                            alpha=1))
                self.signal_se_label_axvline.append(
                    self.signal_ax[1].text(
                        x=int((each[0] - self.current_sec) * self.midata.sf[self.show_idx[0]]),
                        y=self.y_lims[self.show_idx[0]] + self.y_shift[self.show_idx[0]],
                        s=each[2] + "-S", verticalalignment="top",
                        color=identify_startend_color(self.start_end_color_dict, each[2])))

            if self.current_sec <= each[1] <= self.current_sec + self.show_duration:
                for idx, show_ in enumerate(self.show_idx):
                    self.signal_se_label_axvline.append(
                        self.signal_ax[idx + 1].axvline(
                            int((each[1] - self.current_sec) * self.midata.sf[show_]),
                            color="orange", alpha=1))
                self.signal_se_label_axvline.append(
                    self.signal_ax[1].text(
                        x=int((each[1] - self.current_sec) * self.midata.sf[self.show_idx[0]]),
                        y=self.y_lims[self.show_idx[0]] + self.y_shift[self.show_idx[0]],
                        s=each[2] + "-E", verticalalignment="top",
                        horizontalalignment="right", color="orange"))

        if flush:
            self.signal_figure.canvas.draw()
            self.signal_figure.canvas.flush_events()

    def plot_horizontal_line(self, flush=True):
        """Plot the horizontal reference lines."""
        for axhline in self.axhline_horizontal:
            try:
                axhline.remove()
            except Exception:
                pass
        for idx, show_ in enumerate(self.show_idx):
            ch = self.midata.channels[show_]
            sf = self.midata.sf[show_]
            for line_value, color, comment in self.horizontal_line.get(ch, []):
                self.axhline_horizontal.append(
                    self.signal_ax[idx + 1].axhline(line_value, color=color, alpha=1))
                self.axhline_horizontal.append(
                    self.signal_ax[idx + 1].text(
                        x=int(self.show_duration * sf), y=line_value,
                        s=f"{line_value:.2e}",
                        horizontalalignment="left", color=color))

        if flush:
            self.signal_figure.canvas.draw()
            self.signal_figure.canvas.flush_events()

    def plot_hypo(self):
        """Redraw the hypnogram area (one colored segment per sleep state)."""
        # The state-step background only changes when the annotation changes;
        # rebuild it lazily and reuse it across page flips.
        key = None
        if self.mianno is not None:
            key = (id(self.mianno), hash(tuple(self.mianno.sleep_state)))
        if key != self._hypo_key:
            self.hypo_ax.clear()
            self._hypo_transient = []
            # One step segment per consecutive run of the same state, colored
            # with the configured state color for an at-a-glance hypnogram.
            runs = lst2group([i, each] for i, each in enumerate(self.mianno.sleep_state))
            for start, end, state in runs:
                if end <= start:
                    continue
                color = self.state_color_dict.get(state, "#8892a0")
                self._hypo_steps.append(self.hypo_ax.step(
                    range(start, end), [state] * (end - start),
                    where="mid", color=color, linewidth=1.3))

            self.hypo_ax.set_ylim(0, len(list(self.state_map_dict.keys())) + 0.5)
            self.hypo_ax.set_xlim(0, self.total_seconds)
            self.hypo_ax.yaxis.set_ticks(
                list(self.state_map_dict.keys()), list(self.state_map_dict.values()))
            self.hypo_ax.set_xlabel("Time (s)")
            # faint horizontal guides at each state level
            self.hypo_ax.grid(axis="y", alpha=0.25)
            self._hypo_key = key

        # remove the per-flip overlay artists (current-time / event lines)
        for art in self._hypo_transient:
            try:
                art.remove()
            except Exception:
                pass
        self._hypo_transient = []

        try:
            self.hypo_axvline.remove()
        except Exception:
            pass  # axes may have been recreated; a new line is drawn below
        self.hypo_axvline = self.hypo_ax.axvline(
            self.current_sec, color="gray", alpha=0.8)
        self._hypo_transient.append(self.hypo_axvline)

        if self.StartEndRadio.isChecked():
            for each in self.start_end_ms:
                self._hypo_transient.append(
                    self.hypo_ax.axvline(each, color="lime", alpha=1))
        if self.SleepStateRadio.isChecked():
            for each in self.start_end:
                self._hypo_transient.append(
                    self.hypo_ax.axvline(each, color="lime", alpha=1))
        for each in self.mianno.marker:
            self._hypo_transient.append(
                self.hypo_ax.axvline(each[0], color="Red", alpha=1))

        self.hypo_figure.canvas.draw()
        self.hypo_figure.canvas.flush_events()

    def redraw_all(self, second=0):
        """Validate ``second`` and redraw everything."""
        if second + self.show_duration >= self.total_seconds:
            self.current_sec = self.total_seconds - self.show_duration
        elif second <= 0:
            self.current_sec = 0
        else:
            self.current_sec = second

        # Block signals to avoid cyclic value-change operations
        self.ScrollerBar.blockSignals(True)
        self.SecondSpin.blockSignals(True)
        self.DateTimeEdit.blockSignals(True)
        self.ScrollerBar.setValue(self.current_sec)
        self.SecondSpin.setValue(self.current_sec)
        self.DateTimeEdit.setDateTime(self.ac_time + datetime.timedelta(seconds=self.current_sec))
        self.ScrollerBar.blockSignals(False)
        self.SecondSpin.blockSignals(False)
        self.DateTimeEdit.blockSignals(False)
        self.plot_signals()
        self.plot_hypo()

    def fill_channel_listView(self):
        """Fill the channel list view with ``self.midata.channels``."""
        self._updating_ch_list = True
        try:
            self.channel_slm.setChannels(self.midata.channels)
            # only (re)attach the model when needed, otherwise the
            # selection would be cleared on every refresh
            if self.ChListView.model() is not self.channel_slm:
                self.ChListView.setModel(self.channel_slm)
        finally:
            self._updating_ch_list = False

    def _on_channel_list_changed(self, *args):
        """React to any channel-list model change.

        ``ChannelListModel`` supports ``moveRows``, so a drag & drop emits
        ``rowsMoved``; this hook detects the resulting pure reorder (a
        permutation of the channel names) and applies it. Plain text edits
        are left to :meth:`channel_rename`.
        """
        if self._updating_ch_list or self.midata is None:
            return
        try:
            lst = list(self.channel_slm.channels())
        except Exception:
            return
        if len(lst) != self.midata.n_channels:
            return
        if lst == self.midata.channels:
            return
        if sorted(lst) != sorted(self.midata.channels):
            return  # a text edit (rename), not a move
        self.channel_moved(None, 0, len(lst) - 1, None, 0)

    def _apply_channel_order(self, new_order):
        """Reorder the data and view state to match ``new_order``.

        Only the order changes -- channel names and data stay intact.
        """
        spec_name = self.midata.channels[self.current_spectrogram_idx]
        order_idx = [self.midata.channels.index(name) for name in new_order]

        self.midata.reorder_channels(new_order)

        self.y_lims = [self.y_lims[i] for i in order_idx]
        self.y_shift = [self.y_shift[i] for i in order_idx]
        self.horizontal_line = {name: self.horizontal_line.get(name, []) for name in new_order}
        self.current_spectrogram_idx = self.midata.channels.index(spec_name)
        self.show_idx = list(range(self.midata.n_channels))

        self.fill_channel_listView()
        self.redraw_all(second=self.current_sec)

    def channel_moved(self, parent, start, end, destination, row):
        """Reorder the data to match a model move in the channel list."""
        if self._updating_ch_list or self.midata is None:
            return

        new_order = list(self.channel_slm.channels())
        if new_order == self.midata.channels or len(new_order) != self.midata.n_channels:
            return
        self._apply_channel_order(new_order)

    def move_channel(self, direction):
        """Move the selected channel up or down in the list (buttons)."""
        if self.midata is None:
            return
        selected = [r.row() for r in self.ChListView.selectedIndexes()]
        if len(selected) != 1:
            return
        row = selected[0]
        target = row - 1 if direction == "up" else row + 1
        if not (0 <= target < self.midata.n_channels):
            return

        order = list(self.midata.channels)
        item = order.pop(row)
        order.insert(target, item)
        self._apply_channel_order(order)

        # keep the moved item selected (get a fresh selection model --
        # setModel may have recreated it)
        sm = self.ChListView.selectionModel()
        idx = self.channel_slm.index(target)
        self.ChListView.setCurrentIndex(idx)
        if sm is not None:
            sm.select(idx, sm.SelectionFlag.ClearAndSelect)

    def show_marker_list(self):
        """Open the marker list viewer dialog."""
        if self.mianno is None:
            QMessageBox.about(self, "Info", "Load data and annotation first.")
            return
        dialog = EventListDialog(self)
        dialog.show_events(kind="marker")
        dialog.exec()

    def show_start_end_list(self):
        """Open the start-end event list viewer dialog."""
        if self.mianno is None:
            QMessageBox.about(self, "Info", "Load data and annotation first.")
            return
        dialog = EventListDialog(self)
        dialog.show_events(kind="start_end")
        dialog.exec()

    def _sync_state_buttons(self):
        """Keep the Annotation dock state buttons in sync with the state map.

        The original 1-4 buttons (NREM/REM/Wake/Init) from the .ui are
        reused and only restyled/renamed; any extra states (5-10) get
        additional colored buttons in the ``ExtraStatePanel`` (declared in
        the .ui, below them).
        """
        orig = {1: self.NREMBt, 2: self.REMBt, 3: self.WakeBt, 4: self.InitBt}
        self._state_btns = {}

        # clear and (re)fill the panel for extra states 5..10
        extra_grid = self.ExtraStatePanel.layout()
        while extra_grid.count():
            item = extra_grid.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        extra_idx = 0
        for code in sorted(self.state_map_dict):
            name = self.state_map_dict[code]
            color = self.state_color_dict.get(code, "#808080")
            if code in orig:
                bt = orig[code]
            else:
                row, col = divmod(extra_idx, 2)
                extra_idx += 1
                bt = QPushButton()
                bt.clicked.connect(
                    lambda _=False, c=code: self.sleep_state_label(state_code=c))
                extra_grid.addWidget(bt, row, col)
            bt.setText(f"{code}:{name}")
            bt.setStyleSheet(f"background-color:{color}")
            bt.setToolTip(
                f"Label the selected area as {name} "
                f"(shortcut key {code if code < 10 else 0})")
            self._state_btns[code] = bt

    # ------------------------------------------------------------------
    # Interaction
    # ------------------------------------------------------------------
    def radio_recheck(self, radioBt):
        """Reset the selection lines when the label mode changes."""
        if radioBt.text() == "Sleep state":
            self.start_end_ms = []
            self.plot_start_end_line()
        if radioBt.text() == "Start-End":
            self.start_end = []
            self.plot_start_end_line(ms=True)

    def click_signal(self, event):
        """Handle clicks in the signal area (marker / start-end selection).

        The clicked axes identifies the channel (row ``i`` of the signal
        boxes); the x position gives the time.
        """
        if event.inaxes == self.signal_ax[0]:
            return

        # Find the channel row by identity (Axes are not compared by value)
        row = None
        for idx, ax in enumerate(self.signal_ax):
            if ax is event.inaxes:
                row = idx - 1
                break
        if row is None or row < 0 or row >= len(self.show_idx):
            return

        try:
            sf = self.midata.sf[self.show_idx[row]]
            sec = int(event.xdata / sf) + self.current_sec
        except (TypeError, IndexError):
            return

        if self.SleepStateRadio.isChecked():
            if event.button == 3:
                # Right click: remove the line(s) at this second
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
                if len(self.start_end) == 2 and sec + 1 == self.start_end[1]:
                    self.start_end.pop(1)
                    self.plot_start_end_line()
                    return
                return

            if not self.start_end:
                self.start_end.append(sec)
            elif len(self.start_end) == 2:
                self.start_end = [sec]
            elif sec < self.start_end[0]:
                self.start_end = [sec]
            else:
                self.start_end.append(sec + 1)

            self.plot_start_end_line()

        if self.MarkerRadio.isChecked():
            if event.button == 3:
                for each in self.mianno.marker:
                    if abs(each[0] - sec) <= 1:
                        self.mianno.marker.remove(each)
                self.plot_signals()
                self.plot_hypo()
                return

            x = round(event.xdata / sf, 3) + self.current_sec

            self.label_dialog._type = 0
            self.label_dialog.show_contents()
            self.label_dialog.exec()
            if self.label_dialog.closed:
                return

            label_name = self.label_dialog.label_name
            self.mianno.marker.append([x, label_name])
            self.plot_marker_line()

            self.is_saved = False
            self.AnnotationPathLabel.setText("*Annotation path:")

        if self.StartEndRadio.isChecked():
            x = round(event.xdata / sf, 3) + self.current_sec
            if event.button == 3:
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
                if abs(x - self.start_end_ms[1]) <= 1:
                    self.start_end_ms[0] = self.start_end_ms[1]
                    self.start_end_ms.pop(1)
                else:
                    self.start_end_ms = [x]
            else:
                if x < self.start_end_ms[0]:
                    QMessageBox.about(self, "Error", "End should be larger than Start!")
                    return
                self.start_end_ms.append(x)

            self.plot_start_end_line(ms=True)

    def click_hypo(self, event):
        """Jump to the clicked time on the hypnogram."""
        current_sec = int(event.xdata)
        self.redraw_all(second=current_sec)

    def scroller_change(self):
        """Scrollbar value changed."""
        self.ScrollerBar.setDisabled(True)
        current_sec = self.ScrollerBar.value()
        self.redraw_all(second=current_sec)
        self.ScrollerBar.setEnabled(True)

    def next_epoch(self):
        self.redraw_all(second=self.current_sec + 5)

    def previous_epoch(self):
        self.redraw_all(second=self.current_sec - 5)

    def next_page(self):
        self.redraw_all(second=self.current_sec + self.show_duration)

    def previous_page(self):
        self.redraw_all(second=self.current_sec - self.show_duration)

    def SecondSpin_change(self):
        self.redraw_all(second=self.SecondSpin.value())

    def DateTimeEdit_change(self):
        dateTime = self.DateTimeEdit.dateTime().toPython()
        current_sec = int((dateTime - self.ac_time).total_seconds())
        self.redraw_all(second=current_sec)

    # ------------------------------------------------------------------
    # Channel operations
    # ------------------------------------------------------------------
    def channel_rename(self):
        """Rename channels from the list view.

        A pure reorder (a permutation of the names) is not a rename -- it
        is handled by :meth:`_on_channel_list_changed` / :meth:`channel_moved`.
        """
        new_channels = list(self.channel_slm.channels())
        if sorted(new_channels) == sorted(self.midata.channels):
            return  # drag & drop reorder, not a rename

        old_channels = list(self.midata.channels)
        rename_map = {}
        for old, new in zip(old_channels, new_channels):
            if old != new:
                rename_map[old] = new
        if not rename_map:
            return

        # rename_channels may add a "_1" suffix when the target name is
        # already in use, so rebuild horizontal_line by position afterwards.
        self.midata.rename_channels(rename_map)
        final_channels = self.midata.channels
        self.horizontal_line = {
            final_channels[i]: self.horizontal_line.get(old_channels[i], [])
            for i in range(len(final_channels))
        }

        self.fill_channel_listView()
        self.plot_signals()

    def show_chs(self):
        """Show the selected channels."""
        selected_channels = [each.row() for each in self.ChListView.selectedIndexes()]
        if not selected_channels:
            return
        self.show_idx = sorted(selected_channels)
        self.plot_signals()

    def hide_chs(self):
        """Hide the selected channels."""
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
        """Delete the selected channels from the data."""
        selected_channel = [each.row() for each in self.ChListView.selectedIndexes()]
        if not selected_channel:
            return
        box = QMessageBox.question(
            self, "Warning", "You are deleting data!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)

        if box == QMessageBox.StandardButton.Yes:
            if len(selected_channel) == self.midata.n_channels:
                QMessageBox.about(self, "Error", "You can't delete all channels!")
                return

            spec_name = self.midata.channels[self.current_spectrogram_idx]
            for each in sorted(selected_channel, reverse=True):
                self.y_lims[each] = -1
                self.y_shift[each] = -1
                self.horizontal_line.pop(self.midata.channels[each], None)
                self.midata.delete(self.midata.channels[each])

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
        """Zoom in on the selected channels."""
        selected_channel = [each.row() for each in self.ChListView.selectedIndexes()]
        if not selected_channel:
            return
        self.y_lims = [
            lim * 0.9 if idx in selected_channel else lim
            for idx, lim in enumerate(self.y_lims)]
        self.plot_signals(clf=False, replot_axes=selected_channel)

    def scaler_down(self):
        """Zoom out on the selected channels."""
        selected_channel = [each.row() for each in self.ChListView.selectedIndexes()]
        if not selected_channel:
            return
        self.y_lims = [
            lim * 1.1 if idx in selected_channel else lim
            for idx, lim in enumerate(self.y_lims)]
        self.plot_signals(clf=False, replot_axes=selected_channel)

    def multiple_scaler(self):
        """Scale the selected channels by a custom factor."""
        selected_channel = [each.row() for each in self.ChListView.selectedIndexes()]
        scaler_num = self.multipleScalerEditor.value()
        if not selected_channel:
            return
        self.y_lims = [
            lim / scaler_num if idx in selected_channel else lim
            for idx, lim in enumerate(self.y_lims)]
        self.plot_signals(clf=False, replot_axes=selected_channel)

    def shift_up(self):
        """Shift the selected channels up."""
        selected_channel = [each.row() for each in self.ChListView.selectedIndexes()]
        if not selected_channel:
            return
        self.y_shift = [
            shift - self.y_lims[idx] * 0.05 if idx in selected_channel else shift
            for idx, shift in enumerate(self.y_shift)]
        self.plot_signals(clf=False, replot_axes=selected_channel)

    def shift_down(self):
        """Shift the selected channels down."""
        selected_channel = [each.row() for each in self.ChListView.selectedIndexes()]
        if not selected_channel:
            return
        self.y_shift = [
            shift + self.y_lims[idx] * 0.05 if idx in selected_channel else shift
            for idx, shift in enumerate(self.y_shift)]
        self.plot_signals(clf=False, replot_axes=selected_channel)

    def filter_confirm(self):
        """Apply a filter to the selected channel."""
        selected_channel = [each.row() for each in self.ChListView.selectedIndexes()]
        if not selected_channel:
            return
        if len(selected_channel) > 1:
            QMessageBox.about(
                self, "Error",
                "Select one channel to be the default channel for spectrogram.")
            return

        filter_type = self.FilterTypeCombo_dict[self.FilterTypeCombo.currentIndex()]
        low = self.FilterLowSpin.value()
        high = self.FilterHighSpin.value()
        if filter_type in ("bandpass", "bandstop") and low >= high:
            return
        self.midata.filter(
            chans=[self.midata.channels[selected_channel[0]]],
            btype=filter_type, low=low, high=high)
        self.y_lims.append(self.y_lims[selected_channel[0]])
        self.y_shift.append(self.y_shift[selected_channel[0]])

        self.horizontal_line[self.midata.channels[-1]] = []
        self.show_idx.append(self.midata.n_channels - 1)
        self.fill_channel_listView()
        self.redraw_all(second=self.current_sec)

    def FilterTypeCombo_change(self):
        """Enable/disable the filter cut-off spins according to the filter type."""
        if self.FilterTypeCombo.currentIndex() in (0, 3):
            self.FilterHighSpin.setEnabled(True)
            self.FilterLowSpin.setEnabled(True)
        if self.FilterTypeCombo.currentIndex() == 1:
            self.FilterHighSpin.setDisabled(True)
            self.FilterLowSpin.setEnabled(True)
        if self.FilterTypeCombo.currentIndex() == 2:
            self.FilterHighSpin.setEnabled(True)
            self.FilterLowSpin.setDisabled(True)

    def show_spec_window(self):
        """Show the spectrum/spectrogram window for the selected segment."""
        if self.SleepStateRadio.isChecked() and len(self.start_end) == 2 and \
                self.start_end[1] - self.start_end[0] >= 5:
            start_ = self.start_end[0]
            end_ = self.start_end[1]
        elif self.StartEndRadio.isChecked() and len(self.start_end_ms) == 2 and \
                self.start_end_ms[1] - self.start_end_ms[0] >= 5:
            start_ = self.start_end_ms[0]
            end_ = self.start_end_ms[1]
        else:
            QMessageBox.about(
                self, "Error",
                "Please select a start-end larger than 5 seconds.")
            return

        selected_channel = [each.row() for each in self.ChListView.selectedIndexes()]
        if not selected_channel or len(selected_channel) > 1:
            QMessageBox.about(
                self, "Error",
                "Select one channel to show spectral analysis")
            return

        channel = selected_channel[0]
        signal_data = self.midata.signals[channel][
            int(start_ * self.midata.sf[channel]): int(end_ * self.midata.sf[channel])]

        win_sec = int(float(self.config["spec"]["win_length_sec"]))
        nfft = int(float(self.config["spec"]["nfft_sec"]) * self.midata.sf[channel])
        if win_sec > (end_ - start_):
            win_sec = end_ - start_
        if nfft < int(win_sec * self.midata.sf[channel]):
            nfft = int(win_sec * self.midata.sf[channel])

        try:
            freq_range = [float(x) for x in self.config["gui"]["freq_range"].strip("[]").split(",")]
            freq, psd = spectrum(
                signal=signal_data,
                sf=self.midata.sf[channel],
                band=freq_range,
                nfft=nfft,
                gaussian_sigma=float(self.config["spec"]["gaussian_sigma"]),
                win_sec=win_sec,
                relative=False)

            f, t, Sxx = spectrogram(
                signal=signal_data,
                sf=self.midata.sf[channel],
                band=freq_range,
                step=1, win_sec=win_sec, norm=False, nfft=nfft)

            bandPower = band_power(psd=psd, freq=freq,
                                   bands=[[0.5, 4, "delta"], [4, 9, "theta"]])
            ratio = bandPower["delta"] / bandPower["theta"]

            self.spec_window.show_(
                spectrum=[psd, freq],
                spectrogram=[f, t, Sxx],
                percentile_=self.spectrogram_percentile,
                ratio=ratio, start_end=[start_, end_],
                freq_range=freq_range,
                data_path=self.data_path)

            self.spec_window.activateWindow()
            state = self.spec_window.windowState()
            self.spec_window.setWindowState(
                (state & ~Qt.WindowState.WindowMinimized)
                | Qt.WindowState.WindowActive)
            self.spec_window.showNormal()
        except Exception:
            QMessageBox.about(
                self, "Error",
                "An error occurred while generating the spectral analysis.")
            return

    def set_show_duration(self, type_="Combo"):
        """Set the show duration from the combo box or the custom spin box."""
        if type_ == "Combo":
            selected_idx = self.ShowRangeCombo.currentIndex()
            if self.ShowRangeCombo_dict[selected_idx] + self.current_sec >= self.total_seconds:
                self.show_duration = 30
                self.current_sec = 0
                self.ShowRangeCombo.setCurrentIndex(0)
            else:
                self.show_duration = self.ShowRangeCombo_dict[selected_idx]
        if type_ == "Spin":
            show_duration = self.SecondNumSpin.value()
            if show_duration + self.current_sec >= self.total_seconds:
                self.show_duration = 30
                self.current_sec = 0
                self.SecondNumSpin.setValue(30)
            else:
                self.show_duration = show_duration

        self.reset_sec_limit()
        self.redraw_all(second=self.current_sec)
        self.ScrollerBar.setPageStep(self.show_duration)

    def CustomSecondCheck_clicked(self):
        if self.CustomSecondsCheck.isChecked():
            self.ShowRangeCombo.setDisabled(True)
            self.SecondNumSpin.setEnabled(True)
            self.set_show_duration(type_="Spin")
        else:
            self.ShowRangeCombo.setEnabled(True)
            self.SecondNumSpin.setDisabled(True)
            self.set_show_duration(type_="Combo")

    def ShowRangeCombo_changed(self):
        self.set_show_duration(type_="Combo")

    def SecondNumSpin_changed(self):
        self.set_show_duration(type_="Spin")

    # ------------------------------------------------------------------
    # Labeling
    # ------------------------------------------------------------------
    def nrem_label(self):
        self.append_sleep_state(sleep_type=1)

    def rem_label(self):
        self.append_sleep_state(sleep_type=2)

    def wake_label(self):
        self.append_sleep_state(sleep_type=3)

    def init_label(self):
        self.append_sleep_state(sleep_type=4)

    def sleep_state_label(self, state_code=1):
        """Label the selected area with a custom state code (from config)."""
        self.append_sleep_state(sleep_type=state_code)

    def append_sleep_state(self, sleep_type=None):
        """Assign a sleep state to the selected start-end area."""
        if len(self.start_end) != 2:
            QMessageBox.about(
                self, "Info", "Please select a start end area in Sleep state mode")
            return

        self.mianno.sleep_state[self.start_end[0]: self.start_end[1]] = \
            [sleep_type] * (self.start_end[1] - self.start_end[0])

        self.is_saved = False
        self.AnnotationPathLabel.setText("*Annotation path:")
        self.replot_sleep_state_bg(state=sleep_type)
        self.plot_hypo()

    def append_start_end(self):
        """Append a start-end label to the annotation."""
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
        self.mianno.start_end.append(
            [self.start_end_ms[0], self.start_end_ms[1], label_name])
        self.plot_start_end_label_line()

        self.is_saved = False
        self.AnnotationPathLabel.setText("*Annotation path:")

    # ------------------------------------------------------------------
    # Tools / analysis
    # ------------------------------------------------------------------
    def transfer_result(self):
        """Transfer the annotation into an Excel result file."""
        self.transfer_result_dialog.ACTimeEditor.setDateTime(self.ac_time)
        self.transfer_result_dialog.TransferStartTimeEdit.setDateTime(self.ac_time)
        self.transfer_result_dialog.exec()
        if self.transfer_result_dialog.closed:
            return
        self.transfer_result_dialog.transfer(config=self.config,
                                             mianno=self.mianno,
                                             ac_time=self.midata.time)

    def state_spectral(self):
        """Run the per-state spectral analysis."""
        self.state_spectral_dialog.StartTimeEditor.setDateTime(self.ac_time)
        self.state_spectral_dialog.EndTimeEditor.setDateTime(
            self.ac_time + datetime.timedelta(seconds=self.total_seconds))
        self.state_spectral_dialog.dialog_show(channels=self.midata.channels)
        self.state_spectral_dialog.exec()
        if self.state_spectral_dialog.closed:
            return
        self.state_spectral_dialog.spectral_analysis(midata=self.midata,
                                                     mianno=self.mianno,
                                                     config=self.config)

    def add_horizontal_line(self):
        """Add a horizontal reference line."""
        try:
            self.horizontal_line_dialog.horizontal_line = copy.deepcopy(self.horizontal_line)
            self.horizontal_line_dialog.show_chs()
            self.horizontal_line_dialog.midata = self.midata
            self.horizontal_line_dialog.exec()
            if self.horizontal_line_dialog.closed:
                return
            self.horizontal_line = self.horizontal_line_dialog.horizontal_line
            self.plot_horizontal_line()
        except Exception as e:
            logger.error(f"Add horizontal line ERROR: {e}")
            QMessageBox.about(self, "Error", str(e))
            return

    def swa_detection(self):
        """Slow-wave activity detection."""
        try:
            self.swa_detection_dialog.show_chs(self.midata.channels)
            self.swa_detection_dialog.exec()
            if self.swa_detection_dialog.closed:
                return
            swa_lst = self.swa_detection_dialog.swa_detection(
                self.midata, self.mianno, self.config)

            self.mianno._start_end += [[each[0], each[4], "SWA"] for each in swa_lst]
            self.plot_start_end_label_line()
            self.is_saved = False
            self.AnnotationPathLabel.setText("*Annotation path:")
        except Exception as e:
            logger.error(f"SWA_detection ERROR: {e}")
            QMessageBox.about(self, "Error", f"SWA detection ERROR. {e}")
            return

    def spindle_detection(self):
        """Sleep spindle detection."""
        try:
            self.spindel_detection_dialog.show_chs(self.midata.channels)
            self.spindel_detection_dialog.exec()
            if self.spindel_detection_dialog.closed:
                return
            spindle_lst = self.spindel_detection_dialog.spindle_detection(
                self.midata, self.mianno, self.config)

            self.mianno._start_end += [[each[0], each[1], "Spindle"] for each in spindle_lst]
            self.plot_start_end_label_line()
            self.is_saved = False
            self.AnnotationPathLabel.setText("*Annotation path:")
        except Exception as e:
            logger.error(f"Spindel_detection ERROR: {e}")
            QMessageBox.about(self, "Error", "Spindle detection ERROR")
            return

    def auto_stage_LightGBM(self):
        """Auto stage with the LightGBM model."""
        try:
            self.auto_stage_lightGBM_dialog.show_chs(self.midata.channels)
            self.auto_stage_lightGBM_dialog.exec()
            if self.auto_stage_lightGBM_dialog.closed:
                return
            auto_stage_lst, save_anno = self.auto_stage_lightGBM_dialog.auto_stage(
                self.midata, self.mianno)

            limit = min(len(self.mianno._sleep_state), len(auto_stage_lst))
            self.mianno._sleep_state[:limit] = auto_stage_lst[:limit]

            if save_anno:
                self.save_anno()
            self.is_saved = False
            self.AnnotationPathLabel.setText("*Annotation path:")
            self.plot_signals()
            self.plot_hypo()
        except ImportError as e:
            QMessageBox.about(self, "Error", str(e))
            return
        except Exception as e:
            logger.error(f"Auto stage ERROR: {e}")
            QMessageBox.about(self, "Error", "Auto stage ERROR")
            return

    def auto_stage_CausalTransformer(self):
        """Auto stage with the causal-transformer model."""
        try:
            self.auto_stage_causalTransformer_dialog.show_chs(self.midata.channels)
            self.auto_stage_causalTransformer_dialog.exec()
            if self.auto_stage_causalTransformer_dialog.closed:
                return
            auto_stage_lst, save_anno = self.auto_stage_causalTransformer_dialog.auto_stage(
                self.midata, self.mianno)

            limit = min(len(self.mianno._sleep_state), len(auto_stage_lst))
            self.mianno._sleep_state[:limit] = auto_stage_lst[:limit]

            if save_anno:
                self.save_anno()
            self.is_saved = False
            self.AnnotationPathLabel.setText("*Annotation path:")
            self.plot_signals()
            self.plot_hypo()
        except ImportError as e:
            QMessageBox.about(self, "Error", str(e))
            return
        except Exception as e:
            logger.error(f"Auto stage ERROR: {e}")
            QMessageBox.about(self, "Error", "Auto stage ERROR")
            return

    # ------------------------------------------------------------------
    # Saving
    # ------------------------------------------------------------------
    def save_anno(self, just_save=False):
        """Save the annotation to file.

        Parameters
        ----------
        just_save : bool
            Only save without touching the current annotation path.
        """
        if self.anno_path == "":
            anno_path, _ = QFileDialog.getOpenFileName(
                self, "Select annotation file",
                f"{self.config['gui']['openpath']}",
                "txt Files (*.txt *.TXT)")
            if anno_path == "":
                return
            if not just_save:
                self.anno_path = anno_path
                self.AnnoPathEdit.setText(self.anno_path)

        save_thread = SaveThread(file=[self.mianno, self.midata],
                                 file_path=self.anno_path)
        saved = save_thread.save_anno()
        if saved and not just_save:
            self.is_saved = True
            self.AnnotationPathLabel.setText("Annotation path:")
        save_thread.quit()

    def save_data(self):
        """Export (cropped, channel-selected) data to ``.mat``/``.edf``."""
        self.save_data_dialog.fill_midata_params(midata=self.midata)
        self.save_data_dialog.exec()
        if self.save_data_dialog.closed:
            return

        selected_channels = [each.row() for each in
                             self.save_data_dialog.ChannelListView.selectedIndexes()]
        if selected_channels == []:
            selected_channels = list(range(self.midata.n_channels))
        midata_to_save = self.midata.pick_chs(
            [self.midata.channels[each] for each in selected_channels])

        start_sec = 0
        end_sec = self.midata.duration

        if self.save_data_dialog.CropDataStartCheckBox.isChecked():
            start_time = self.save_data_dialog.CropStartTimeEditor.dateTime().toPython()
            midata_to_save._time = start_time.strftime("%Y%m%d-%H:%M:%S")
            start_sec = int(datetime.timedelta.total_seconds(start_time - self.ac_time))
            if start_sec < 0:
                start_sec = 0

        if self.save_data_dialog.CropDataEndCheckBox.isChecked():
            end_time = self.save_data_dialog.CropEndTimeEditor.dateTime().toPython()
            end_sec = int(datetime.timedelta.total_seconds(end_time - self.ac_time))
            if end_sec > self.midata.duration:
                end_sec = self.midata.duration

        if end_sec <= start_sec:
            start_sec = 0
            end_sec = self.midata.duration

        midata_to_save = midata_to_save.crop([start_sec, end_sec])

        data_path, _ = QFileDialog.getSaveFileName(
            self, "Select a file to save data",
            f"{self.config['gui']['openpath']}_misleep_saved",
            "*mat Files (*.mat *.MAT);;*edf Files (*.edf *.EDF);")
        if data_path == "":
            return

        save_thread = SaveThread(file=midata_to_save, file_path=data_path)
        saved = save_thread.save_data()
        if saved:
            QMessageBox.about(self, "Info", f"Data Saved to {data_path}")
        else:
            QMessageBox.about(self, "Error", "Data save ERROR")
        save_thread.quit()

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------
    def open_settings_dialog(self):
        """Open the in-application settings dialog."""
        dialog = SettingsDialog(self)
        dialog.exec()

    def apply_settings(self):
        """Apply the current configuration to the running application.

        Called after the settings dialog saves changes, so that state
        names/colors, labels and spectral defaults take effect
        immediately without restarting MiSleep.
        """
        gui = self.config["gui"]

        # Apply a theme change (chosen in the settings dialog) immediately
        new_theme = gui.get("theme", fallback="light")
        if new_theme in THEMES and new_theme != self._theme_name:
            self._theme_name = new_theme
            app = QApplication.instance()
            if app is not None:
                apply_theme(app, new_theme)
            retheme_figures(new_theme)
            self._set_plot_colors()
            self._update_theme_action()

        # Reload the parsed dictionaries
        self.state_map_dict = {int(key): value for key, value
                               in json.loads(gui["statemap"]).items()}
        self.state_color_dict = {int(key): value for key, value
                                 in json.loads(gui["statecolor"]).items()}
        self.start_end_color_dict = dict(
            json.loads(gui["startendcolor"].replace("'", '"')).items())

        # Rebuild the state-label buttons (names/colors/extra states)
        self._sync_state_buttons()

        # Refresh the label picker lists
        self.label_dialog.marker_label = [
            each[1:-1] for each in gui["marker"][1:-1].split(", ")]
        self.label_dialog.start_end_label = [
            each[1:-1] for each in gui["startend"][1:-1].split(", ")]

        # Refresh spectral defaults used by the state-spectral dialog
        self.state_spectral_dialog.GaussianSpinBox.setValue(
            float(self.config["spec"]["gaussian_sigma"]))
        self.state_spectral_dialog.WinLengthSpinBox.setValue(
            float(self.config["spec"]["win_length_sec"]))
        self.state_spectral_dialog.nfftSpinBox.setValue(
            int(float(self.config["spec"]["nfft_sec"])))

        # Update the annotation state map if one is loaded
        if isinstance(self.mianno, MiAnnotation):
            self.mianno._state_map = self.state_map_dict

        # Redraw with the new colors / frequency range (skip before data loads)
        if self.midata is not None and self.mianno is not None:
            self.redraw_all(second=self.current_sec)
        else:
            logger.info("Settings applied; they will take effect after loading data.")

    def pupup_config(self):
        """Open the user configuration file with the system editor."""
        import platform
        import subprocess

        path = str(user_config_path())
        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(path)
            elif system == "Darwin":
                subprocess.run(["open", path])
            elif system == "Linux":
                subprocess.run(["xdg-open", path])
        except Exception as e:
            logger.error(f"Open config.ini ERROR: {e}")
            QMessageBox.about(self, "Error", f"Open config.ini ERROR: {e}")

    def auto_save(self):
        """Auto-save the annotation every 5 minutes when modified."""
        if not self.is_saved:
            self.save_anno()
        self.save_timer.start(5 * 60 * 1000)

    def save_config(self, config_dict):
        """Persist GUI configuration changes to the user config file."""
        for key, value in config_dict.items():
            self.config.set("gui", key, value)
        save_config(self.config)

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------
    def keyPressEvent(self, event):
        """Number keys label the selected area with that state.

        Keys 1-9 map to states 1-9; key 0 maps to state 10 (when defined),
        supporting up to ten states.
        """
        if Qt.Key.Key_0 <= event.key() <= Qt.Key.Key_9:
            num = int(event.text())
            state = 10 if num == 0 else num
            if state in self.state_map_dict.keys():
                self.sleep_state_label(state_code=state)
        else:
            QWidget.keyPressEvent(self, event)

    def closeEvent(self, event):
        """Ask for confirmation when there are unsaved labels."""
        if not self.is_saved:
            box = QMessageBox.question(
                self, "Warning",
                "Your labels haven't been saved, discard?\n"
                "Yes: Save and quit\nNo: Discard\nCancel: Nothing",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Yes)

            if box == QMessageBox.StandardButton.Yes:
                self.save_anno()
                event.accept()
            elif box == QMessageBox.StandardButton.No:
                event.accept()
            else:
                event.ignore()


# Backward-compatible alias
main_window = MainWindow
