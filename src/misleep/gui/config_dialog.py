# -*- coding: UTF-8 -*-
"""In-application settings dialog.

Lets the user edit the MiSleep configuration from inside the GUI
(state names & colors, marker color, annotation labels, spectral defaults,
...). Changes are saved to the per-user configuration
file and **applied immediately** to the running application -- no
restart needed.
"""

import json

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from misleep.config import save_config
from misleep.gui.qt_utils import app_icon


def _contrast_text(color: QColor) -> str:
    """Return black or white text depending on the background luminance."""
    lum = 0.299 * color.red() + 0.587 * color.green() + 0.114 * color.blue()
    return "#000000" if lum > 150 else "#ffffff"


class ColorButton(QPushButton):
    """A rounded color swatch that opens a color picker when clicked."""

    def __init__(self, color="#ffffff", parent=None):
        super().__init__(parent)
        self._color = QColor(color)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(64, 26)
        self.setToolTip("Click to choose a color")
        self.set_color(self._color)
        self.clicked.connect(self._pick)

    def _pick(self):
        c = QColorDialog.getColor(self._color, self, "Select color")
        if c.isValid():
            self.set_color(c)

    def set_color(self, color):
        self._color = QColor(color)
        hex_name = self._color.name().upper()
        self.setText(hex_name)
        self.setFont(self.font())
        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {self._color.name()};
                color: {_contrast_text(self._color)};
                border: 2px solid rgba(0, 0, 0, 60%);
                border-radius: 4px;
                font-size: 8pt;
                font-weight: bold;
                padding: 0px;
            }}
            QPushButton:hover {{
                border: 2px solid #000000;
            }}
            QPushButton:pressed {{
                background-color: {self._color.darker(120).name()};
            }}
            """
        )

    def color(self) -> QColor:
        return self._color


class _ListEditor(QWidget):
    """A small editable string list (add / delete / edit items)."""

    def __init__(self, values, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.list = QListWidget()
        self.list.addItems(values)
        layout.addWidget(self.list, 1)

        btns = QVBoxLayout()
        add_bt = QPushButton("Add")
        del_bt = QPushButton("Delete")
        add_bt.clicked.connect(self._add)
        del_bt.clicked.connect(self._delete)
        btns.addWidget(add_bt)
        btns.addWidget(del_bt)
        btns.addStretch(1)
        layout.addLayout(btns)

    def _add(self):
        item = QListWidgetItem("new label")
        self.list.addItem(item)
        self.list.setCurrentItem(item)
        self.list.editItem(item)

    def _delete(self):
        row = self.list.currentRow()
        if row >= 0:
            self.list.takeItem(row)

    def values(self):
        return [self.list.item(i).text() for i in range(self.list.count())]


class SettingsDialog(QDialog):
    """Edit and immediately apply the MiSleep configuration."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._main = parent
        self.config = parent.config

        self.setWindowTitle("MiSleep settings")
        self.resize(640, 560)
        self.setWindowIcon(app_icon())

        tabs = QTabWidget()
        tabs.addTab(self._build_states_tab(), "Sleep states")
        tabs.addTab(self._build_colors_tab(), "Colors")
        tabs.addTab(self._build_labels_tab(), "Labels")
        tabs.addTab(self._build_spectral_tab(), "Spectral")
        tabs.addTab(self._build_general_tab(), "General")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(tabs)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        open_bt = QPushButton("Open file…")
        open_bt.clicked.connect(self._open_file)
        apply_bt = QPushButton("Apply")
        apply_bt.clicked.connect(self._apply)
        ok_bt = QPushButton("OK")
        ok_bt.clicked.connect(self._ok)
        cancel_bt = QPushButton("Cancel")
        cancel_bt.clicked.connect(self.reject)
        for b in (open_bt, apply_bt, ok_bt, cancel_bt):
            btn_row.addWidget(b)

        layout = QVBoxLayout(self)
        layout.addWidget(scroll, 1)
        layout.addLayout(btn_row)

        self._load_from_config()

    # ------------------------------------------------------------------
    # Tab builders
    # ------------------------------------------------------------------
    def _build_states_tab(self):
        self._state_rows = {}  # code -> (name_edit, color_button)
        box = QGroupBox("Sleep states")
        form = QFormLayout(box)
        hint = QLabel("State codes, names and background colors used in the "
                      "signal panel and hypnogram. Up to 10 states "
                      "(keys 0-9 label the selected area).")
        hint.setWordWrap(True)
        form.addRow(hint)
        self._state_frame = QVBoxLayout()
        form.addRow(self._state_frame)

        btn_row = QHBoxLayout()
        add_bt = QPushButton("Add state")
        rem_bt = QPushButton("Remove state")
        add_bt.setToolTip("Add a state with the next free code (1-10)")
        rem_bt.setToolTip("Remove the highest state")
        add_bt.clicked.connect(self._add_state)
        rem_bt.clicked.connect(self._remove_state)
        btn_row.addWidget(add_bt)
        btn_row.addWidget(rem_bt)
        btn_row.addStretch(1)
        form.addRow(btn_row)
        return box

    def _add_state_row(self, code, name, color):
        """Append one state row (code, name edit, color swatch)."""
        row = QWidget()
        h = QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)
        h.addWidget(QLabel(f"State {code}:"))
        name_edit = QLineEdit(name)
        name_edit.setMinimumWidth(140)
        name_edit.setMaximumWidth(220)
        h.addWidget(name_edit)
        color_bt = ColorButton(color)
        h.addWidget(color_bt)
        h.addStretch(1)
        self._state_frame.addWidget(row)
        self._state_rows[int(code)] = (name_edit, color_bt)

    def _add_state(self):
        used = set(self._state_rows.keys())
        free = [c for c in range(1, 11) if c not in used]
        if not free:
            QMessageBox.information(self, "MiSleep", "Maximum of 10 states.")
            return
        self._add_state_row(free[0], f"State {free[0]}", "#808080")

    def _remove_state(self):
        if len(self._state_rows) <= 1:
            QMessageBox.information(self, "MiSleep", "Keep at least one state.")
            return
        code = max(self._state_rows)
        row_widget = self._state_rows[code][0].parentWidget()
        self._state_frame.removeWidget(row_widget)
        row_widget.deleteLater()
        del self._state_rows[code]

    def _build_colors_tab(self):
        page = QWidget()
        page_layout = QVBoxLayout(page)
        box = QGroupBox("Marker color")
        line_form = QFormLayout(box)
        self._marker_line_bt = ColorButton()
        self._marker_line_bt.setToolTip(
            "Marker color in both the signal panel and hypnogram")
        line_form.addRow("Marker:", self._marker_line_bt)
        page_layout.addWidget(box)
        page_layout.addStretch(1)
        return page

    def _build_labels_tab(self):
        box = QGroupBox("Label lists")
        layout = QVBoxLayout(box)

        layout.addWidget(QLabel("Marker labels (single time-point events):"))
        self._marker_editor = _ListEditor([])
        layout.addWidget(self._marker_editor)

        layout.addWidget(QLabel("Start-End labels (events with a duration):"))
        self._se_editor = _ListEditor([])
        layout.addWidget(self._se_editor)
        return box

    def _build_spectral_tab(self):
        box = QGroupBox("Spectral analysis defaults")
        form = QFormLayout(box)

        self._freq_low = QDoubleSpinBox()
        self._freq_low.setRange(0, 500)
        self._freq_low.setDecimals(2)
        self._freq_high = QDoubleSpinBox()
        self._freq_high.setRange(0, 500)
        self._freq_high.setDecimals(2)
        form.addRow("Frequency range (Hz):", self._freq_low)
        form.addRow("", self._freq_high)

        self._win_length = QDoubleSpinBox()
        self._win_length.setRange(1, 3600)
        self._win_length.setDecimals(1)
        form.addRow("Window length (s):", self._win_length)

        self._nfft = QDoubleSpinBox()
        self._nfft.setRange(1, 3600)
        self._nfft.setDecimals(1)
        form.addRow("nfft (s):", self._nfft)

        self._gaussian = QDoubleSpinBox()
        self._gaussian.setRange(0, 100)
        self._gaussian.setDecimals(2)
        form.addRow("Gaussian smoothing σ:", self._gaussian)
        return box

    def _build_general_tab(self):
        box = QGroupBox("General")
        form = QFormLayout(box)

        self._bg_alpha = QDoubleSpinBox()
        self._bg_alpha.setRange(0, 1)
        self._bg_alpha.setSingleStep(0.05)
        self._bg_alpha.setDecimals(2)
        form.addRow("State background alpha:", self._bg_alpha)

        self._hypno_alpha = QDoubleSpinBox()
        self._hypno_alpha.setRange(0.15, 1.0)
        self._hypno_alpha.setSingleStep(0.05)
        self._hypno_alpha.setDecimals(2)
        self._hypno_alpha.setToolTip(
            "Lower values make state bands lighter so marker lines remain visible.")
        form.addRow("Hypnogram state alpha:", self._hypno_alpha)

        path_row = QHBoxLayout()
        self._openpath = QLineEdit()
        browse_bt = QPushButton("Browse…")
        browse_bt.clicked.connect(self._browse_path)
        path_row.addWidget(self._openpath, 1)
        path_row.addWidget(browse_bt)
        form.addRow("Default open path:", path_row)

        self._theme_combo = QComboBox()
        self._theme_combo.addItems(["light", "dark"])
        self._theme_combo.setToolTip(
            "Applies immediately: widgets and plots switch together.")
        form.addRow("Theme:", self._theme_combo)

        self._tone_combo = QComboBox()
        self._tone_combo.addItems(["black", "pink", "blue", "khaki"])
        self._tone_combo.setToolTip(
            "Chrome / accent color scheme (independent of light/dark mode).")
        form.addRow("Color scheme:", self._tone_combo)

        return box

    # ------------------------------------------------------------------
    # Load / collect / save
    # ------------------------------------------------------------------
    def _load_from_config(self):
        gui = self.config["gui"]
        spec = self.config["spec"]

        # Sleep states (dynamic: one row per state code, up to 10)
        while self._state_frame.count():
            item = self._state_frame.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        statemap = json.loads(gui["statemap"])
        statecolor = json.loads(gui["statecolor"])
        for code in sorted(statemap, key=int):
            self._add_state_row(int(code), str(statemap[code]),
                                str(statecolor.get(code, "#808080")))

        # Label lists
        self._marker_editor.list.clear()
        self._marker_editor.list.addItems(
            [each[1:-1] for each in gui["marker"][1:-1].split(", ")])
        self._se_editor.list.clear()
        self._se_editor.list.addItems(
            [each[1:-1] for each in gui["startend"][1:-1].split(", ")])

        # Spectral
        low, high = (float(x) for x in gui["freq_range"].strip("[]").split(","))
        self._freq_low.setValue(low)
        self._freq_high.setValue(high)
        self._win_length.setValue(float(spec["win_length_sec"]))
        self._nfft.setValue(float(spec["nfft_sec"]))
        self._gaussian.setValue(float(spec["gaussian_sigma"]))

        # General
        self._bg_alpha.setValue(float(gui["statecolorbgalpha"]))
        self._hypno_alpha.setValue(float(gui.get("hypnogramstatealpha", "0.55")))
        self._openpath.setText(gui["openpath"])
        self._theme_combo.setCurrentText(gui.get("theme", "light"))
        self._tone_combo.setCurrentText(gui.get("color_tone", "black"))
        self._marker_line_bt.set_color(
            gui.get("markerlinecolor", "red").strip("\"'"))

    def _browse_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select default folder",
                                                self._openpath.text())
        if path:
            self._openpath.setText(path)

    def _open_file(self):
        if self._main is not None:
            self._main.pupup_config()

    # ------------------------------------------------------------------
    # Apply / save
    # ------------------------------------------------------------------
    def _collect(self) -> dict:
        """Return {section: {key: value}} with the new configuration."""
        statemap = {str(code): name_edit.text().strip()
                    for code, (name_edit, _) in self._state_rows.items()}
        statecolor = {str(code): bt.color().name()
                      for code, (_, bt) in self._state_rows.items()}
        return {
            "gui": {
                "statemap": json.dumps(statemap),
                "statecolor": json.dumps(statecolor),
                "marker": str(self._marker_editor.values()),
                "startend": str(self._se_editor.values()),
                "statecolorbgalpha": str(self._bg_alpha.value()),
                "hypnogramstatealpha": str(self._hypno_alpha.value()),
                "freq_range": json.dumps([self._freq_low.value(), self._freq_high.value()]),
                "openpath": self._openpath.text(),
                "theme": self._theme_combo.currentText(),
                "color_tone": self._tone_combo.currentText(),
                "spectrogram_cmap": "jet",
                "markerlinecolor": self._marker_line_bt.color().name(),
            },
            "spec": {
                "win_length_sec": str(self._win_length.value()),
                "nfft_sec": str(self._nfft.value()),
                "gaussian_sigma": str(self._gaussian.value()),
            },
        }

    def _save(self):
        for section, values in self._collect().items():
            for key, value in values.items():
                self.config.set(section, key, value)
        save_config(self.config)

    def _apply(self):
        self._save()
        if self._main is not None:
            self._main.apply_settings()
        QMessageBox.information(self, "MiSleep",
                                "Settings saved and applied.")

    def _ok(self):
        self._save()
        if self._main is not None:
            self._main.apply_settings()
        self.accept()
