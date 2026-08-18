# -*- coding: UTF-8 -*-
"""Theme system for the MiSleep GUI: light & dark Qt styling + matplotlib theming.

Everything visual lives here so the look of MiSleep is:

* **consistent** -- one palette drives the Qt widgets *and* the matplotlib
  canvases, so the plot area and the surrounding chrome feel like a single
  designed surface,
* **precise** -- every control has an explicit hover / pressed / focus /
  disabled state, a calm rounded geometry and a clear accent colour,
* **portable** -- sizes are expressed in ``pt`` / logical pixels (Qt scales
  them with the display DPI), fonts are picked per platform, and the same
  stylesheet renders on Windows, macOS and Linux (a ``Fusion`` base style is
  used so the QSS result is identical everywhere),
* **data friendly** -- the matplotlib theme keeps the plots on high-contrast
  surfaces with soft grids and legible ticks.

The public API is small::

    apply_theme(app, "light")     # full theme: style + fonts + matplotlib
    apply_theme(app, "dark")
    retheme_figures("dark")       # restyle every open figure after a toggle
    apply_app_style(app)          # backward compatible alias -> light theme

The previous behaviour of :func:`apply_app_style` (a fixed light stylesheet)
is preserved for compatibility.
"""

from __future__ import annotations

import copy
import sys
from string import Template

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

# ---------------------------------------------------------------------------
# Palettes
# ---------------------------------------------------------------------------

THEMES = {
    "light": {
        "name": "Light",
        # surfaces
        "window": "#d8dee8",
        "surface": "#f2f4f7",
        "surface_alt": "#cfd7e3",
        "input": "#f8f9fb",
        "disabled_bg": "#d9dfe8",
        # lines
        "border": "#aeb9c8",
        "border_strong": "#75859b",
        "button_top": "#f8f9fb",
        "button_bottom": "#cbd4e0",
        # text
        "text": "#141d2b",
        "text_secondary": "#4a5a70",
        "text_disabled": "#97a3b3",
        # accent (indigo)
        "accent": "#4b56d9",
        "accent_hover": "#3d47c2",
        "accent_pressed": "#333ba6",
        "accent_soft": "#e2e7fc",
        "accent_soft_2": "#d4dbfa",
        # semantic
        "danger": "#dc3d43",
        "danger_hover": "#c43339",
        "success": "#148a5e",
        # misc
        "tooltip_bg": "#1c2736",
        "tooltip_text": "#f4f7fb",
        "scroll_handle": "#aeb9cb",
        "scroll_handle_hover": "#8b9ab2",
        "slider_groove": "#cfd8e6",
        # matplotlib / plot area
        "plot": {"trace": "#0d1524", "grid": "#2f9d74", "bg": "#ffffff"},
        "mpl": {
            "figure.facecolor": "#d8dee8",
            "axes.facecolor": "#ffffff",
            "axes.edgecolor": "#a9b6c9",
            "axes.labelcolor": "#141d2b",
            "xtick.color": "#4a5a70",
            "ytick.color": "#4a5a70",
            "text.color": "#141d2b",
            "grid.color": "#dbe2ec",
            "savefig.facecolor": "#ffffff",
        },
    },
    "dark": {
        "name": "Dark",
        # surfaces
        "window": "#10151f",
        "surface": "#171e2b",
        "surface_alt": "#1e2736",
        "input": "#131a25",
        "disabled_bg": "#171e2b",
        # lines
        "border": "#2c374a",
        "border_strong": "#596984",
        "button_top": "#273247",
        "button_bottom": "#192230",
        # text
        "text": "#eef2f9",
        "text_secondary": "#9aa8bc",
        "text_disabled": "#5b6a80",
        # accent (indigo)
        "accent": "#7a84f0",
        "accent_hover": "#959df5",
        "accent_pressed": "#616bd9",
        "accent_soft": "#28304f",
        "accent_soft_2": "#313b60",
        # semantic
        "danger": "#f0606b",
        "danger_hover": "#f27c85",
        "success": "#2bc48a",
        # misc
        "tooltip_bg": "#2c374a",
        "tooltip_text": "#eef2f9",
        "scroll_handle": "#414e68",
        "scroll_handle_hover": "#5a6a8a",
        "slider_groove": "#2c374a",
        # matplotlib / plot area
        "plot": {"trace": "#d9e3f2", "grid": "#3fae85", "bg": "#101824"},
        "mpl": {
            "figure.facecolor": "#10151f",
            "axes.facecolor": "#101824",
            "axes.edgecolor": "#414e68",
            "axes.labelcolor": "#eef2f9",
            "xtick.color": "#9aa8bc",
            "ytick.color": "#9aa8bc",
            "text.color": "#eef2f9",
            "grid.color": "#232f41",
            "savefig.facecolor": "#101824",
        },
    },
}

# Color-tone presets are independent from light/dark mode.  They change the
# application chrome and accent colors while keeping data/state colors under
# the user's explicit control in Settings.
COLOR_TONES = {
    "black": {
        "name": "Black / Gray",
        "light": {
            "window": "#d6d6d6", "surface": "#f0f0f0",
            "surface_alt": "#c9c9c9", "input": "#f8f8f8",
            "disabled_bg": "#d9d9d9", "border": "#aaaaaa",
            "border_strong": "#666a70", "button_top": "#fafafa",
            "button_bottom": "#c8c8c8", "text": "#151515",
            "text_secondary": "#414141", "text_disabled": "#858585",
            "accent": "#3c3f44", "accent_hover": "#24272b",
            "accent_pressed": "#111315", "accent_soft": "#d3d3d3",
            "accent_soft_2": "#bdbdbd", "scroll_handle": "#969696",
            "scroll_handle_hover": "#707070", "slider_groove": "#bcbcbc",
            "plot": {"grid": "#737373"},
            "mpl": {"figure.facecolor": "#d6d6d6",
                    "axes.edgecolor": "#8a8a8a", "xtick.color": "#414141",
                    "ytick.color": "#414141", "grid.color": "#d0d0d0"},
        },
        "dark": {
            "accent": "#aeb2b8", "accent_hover": "#d0d2d5",
            "accent_pressed": "#858a91", "accent_soft": "#303236",
            "accent_soft_2": "#3c3f44", "text_secondary": "#b4b4b4",
            "plot": {"grid": "#777b80"},
        },
    },
    "pink": {
        "name": "Pink",
        "light": {
            "window": "#ded4d8", "surface": "#f5f0f2",
            "surface_alt": "#d8c6cd", "input": "#fbf8f9",
            "disabled_bg": "#e2dadd", "border": "#bca5ae",
            "border_strong": "#8d6f7b", "button_top": "#fffafb",
            "button_bottom": "#d9c4cc", "text": "#241b1f",
            "text_secondary": "#604b54", "text_disabled": "#9d8991",
            "accent": "#a63f69", "accent_hover": "#862d51",
            "accent_pressed": "#68213e", "accent_soft": "#ead1db",
            "accent_soft_2": "#ddb8c7", "scroll_handle": "#b88b9d",
            "scroll_handle_hover": "#996a7d", "slider_groove": "#d6bbc6",
            "plot": {"grid": "#a85777"},
            "mpl": {"figure.facecolor": "#ded4d8",
                    "axes.edgecolor": "#aa8b98", "xtick.color": "#604b54",
                    "ytick.color": "#604b54", "grid.color": "#eadde2"},
        },
        "dark": {"accent": "#df7da4", "accent_hover": "#ee9fbe",
                 "accent_pressed": "#bd5f85", "accent_soft": "#482a37",
                 "accent_soft_2": "#593344"},
    },
    "blue": {
        "name": "Blue",
        "light": {},
        "dark": {},
    },
    "khaki": {
        "name": "Khaki",
        "light": {
            "window": "#ddd9c9", "surface": "#f3f1e8",
            "surface_alt": "#d4cfb8", "input": "#faf9f3",
            "disabled_bg": "#e0ddcf", "border": "#b8af8e",
            "border_strong": "#82785b", "button_top": "#fbfaf3",
            "button_bottom": "#d2ccb3", "text": "#242117",
            "text_secondary": "#5d5742", "text_disabled": "#99927b",
            "accent": "#71663a", "accent_hover": "#5a512d",
            "accent_pressed": "#40391e", "accent_soft": "#e2ddc4",
            "accent_soft_2": "#d2c9a6", "scroll_handle": "#aaa17f",
            "scroll_handle_hover": "#8c825f", "slider_groove": "#cbc4a7",
            "plot": {"grid": "#847a49"},
            "mpl": {"figure.facecolor": "#ddd9c9",
                    "axes.edgecolor": "#9f9676", "xtick.color": "#5d5742",
                    "ytick.color": "#5d5742", "grid.color": "#e3dfd0"},
        },
        "dark": {"accent": "#c4b76f", "accent_hover": "#d8cd8d",
                 "accent_pressed": "#9f944f", "accent_soft": "#3d3928",
                 "accent_soft_2": "#4b4630"},
    },
    "blue": {
        "name": "Blue",
        "light": {
            "window": "#d6dde8", "surface": "#eef3f9",
            "surface_alt": "#c9d6e6", "input": "#f7fafd",
            "disabled_bg": "#dde4ee", "border": "#a9bcd4",
            "border_strong": "#6f87a5", "button_top": "#fafcfe",
            "button_bottom": "#c2d2e6", "text": "#16202e",
            "text_secondary": "#41536b", "text_disabled": "#8b9ab0",
            "accent": "#2f5f9e", "accent_hover": "#274f85",
            "accent_pressed": "#1e3f6b", "accent_soft": "#d4e2f3",
            "accent_soft_2": "#c0d4ec", "scroll_handle": "#8fa6c2",
            "scroll_handle_hover": "#6d87a8", "slider_groove": "#b9cbe2",
            "plot": {"grid": "#3e76b0"},
            "mpl": {"figure.facecolor": "#d6dde8",
                    "axes.edgecolor": "#7f96b4", "xtick.color": "#41536b",
                    "ytick.color": "#41536b", "grid.color": "#dfe7f1"},
        },
        "dark": {"accent": "#6d9fd8", "accent_hover": "#8cb6e8",
                 "accent_pressed": "#5182bd", "accent_soft": "#23344d",
                 "accent_soft_2": "#2b405f"},
    },
}


def resolved_theme(theme_name: str = "light", tone_name: str = "black") -> dict:
    """Return a theme with the selected color-tone overrides applied."""
    theme_name = theme_name if theme_name in THEMES else "light"
    tone_name = tone_name if tone_name in COLOR_TONES else "black"
    result = copy.deepcopy(THEMES[theme_name])
    for key, value in COLOR_TONES[tone_name][theme_name].items():
        if isinstance(value, dict):
            result[key].update(value)
        else:
            result[key] = value
    return result

#: Buttons that act as *primary* actions get the accent colour.
_PRIMARY_BUTTONS = (
    "SaveLabelBt", "FilterConfirmBt", "MultipleScalerConfirmBt",
    "PlotSpecBt", "LabelBt",
)

#: Buttons that destroy things get the danger colour.
_DANGER_BUTTONS = ("DeleteChBt",)

_PRIMARY_SELECTOR = ", ".join(f"#{name}" for name in _PRIMARY_BUTTONS)
_DANGER_SELECTOR = ", ".join(f"#{name}" for name in _DANGER_BUTTONS)


def _state_selector(names, state):
    """Apply a pseudo-state to every selector in a selector group."""
    return ", ".join(f"#{name}:{state}" for name in names)


def font_families() -> list[str]:
    """Return the recommended font stack for the current platform."""
    if sys.platform == "win32":
        return ["Segoe UI", "Microsoft YaHei UI", "PingFang SC",
                "Noto Sans CJK SC", "Arial"]
    if sys.platform == "darwin":
        return ["SF Pro Text", "PingFang SC", "Helvetica Neue", "Arial"]
    return ["Noto Sans", "DejaVu Sans", "Liberation Sans", "sans-serif"]


# ---------------------------------------------------------------------------
# Qt stylesheet
# ---------------------------------------------------------------------------

_STYLESHEET_TEMPLATE = Template("""
/* ================= MiSleep theme ================= */

QMainWindow, QDialog, QMessageBox, QInputDialog,
QColorDialog, QFileDialog, QFontDialog {
    background-color: $window;
}

QWidget {
    font-size: 9.5pt;
    color: $text;
}

/* ---------------- menu bar & menus ---------------- */
QMenuBar {
    background-color: $window;
    border-bottom: 1px solid $border;
    padding: 2px 4px;
}
QMenuBar::item {
    background: transparent;
    padding: 4px 10px;
    border-radius: 0px;
    color: $text;
}
QMenuBar::item:selected {
    background: $accent_soft;
    color: $text;
}
QMenuBar::item:pressed {
    background: $accent_soft_2;
}

QMenu {
    background-color: $surface;
    border: 1px solid $border;
    border-radius: 0px;
    padding: 5px;
}
QMenu::item {
    padding: 5px 26px 5px 10px;
    border-radius: 0px;
    color: $text;
}
QMenu::item:selected {
    background: $accent_soft;
    color: $text;
}
QMenu::item:disabled {
    color: $text_disabled;
}
QMenu::separator {
    height: 1px;
    background: $border;
    margin: 5px 8px;
}
QMenu::indicator {
    width: 14px;
    height: 14px;
}

/* ---------------- toolbar ---------------- */
QToolBar {
    background: $surface;
    border-bottom: 1px solid $border;
    spacing: 3px;
    padding: 4px 8px;
}
QToolBar::separator {
    background: $border;
    width: 1px;
    margin: 5px 8px;
}
QToolButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 $button_top, stop:1 $button_bottom);
    border: 1px solid $border_strong;
    border-radius: 4px;
    padding: 3px 8px;
    color: $text;
}
QToolButton:hover {
    background: $accent_soft;
}
QToolButton:pressed, QToolButton:checked {
    background: $accent_soft_2;
    color: $accent;
}
QToolButton:disabled {
    color: $text_disabled;
}

/* ---------------- buttons ---------------- */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 $button_top, stop:1 $button_bottom);
    border: 1px solid $border_strong;
    border-radius: 4px;
    padding: 2px 9px;
    color: $text;
    min-height: 20px;
    max-height: 24px;
}
QPushButton:hover {
    background: $surface_alt;
    border-color: $accent;
}
QPushButton:pressed {
    background: $accent_soft_2;
}
QPushButton:focus {
    border-color: $accent;
}
QPushButton:disabled {
    color: $text_disabled;
    background: $disabled_bg;
    border-color: $border;
}
QPushButton:checked {
    background: $accent_soft;
    border-color: $accent;
    color: $accent;
}
QPushButton[default="true"] {
    background: $accent;
    border-color: $accent;
    color: #ffffff;
}
QPushButton[default="true"]:hover {
    background: $accent_hover;
    border-color: $accent_hover;
}
QPushButton[default="true"]:pressed {
    background: $accent_pressed;
    border-color: $accent_pressed;
}

/* channel-move arrows share a row and expand like Show/Hide/Delete */
#MoveUpBt, #MoveDownBt {
    min-height: 20px;
    max-height: 24px;
    min-width: 52px;
    padding: 0px;
    font-size: 10pt;
}

/* primary actions */
$_primary {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 $accent, stop:1 $accent_pressed);
    border-color: $accent;
    color: #ffffff;
    font-weight: 600;
}
$_primary_hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 $accent_hover, stop:1 $accent);
    border-color: $accent_hover;
}
$_primary_pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 $accent_pressed, stop:1 $accent_pressed);
    border-color: $accent_pressed;
}
$_primary_disabled {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 $disabled_bg, stop:1 $disabled_bg);
    border-color: $border;
    color: $text_disabled;
    font-weight: 400;
}

/* destructive actions */
$_danger {
    background: $surface;
    border-color: $danger;
    color: $danger;
}
$_danger_hover {
    background: $danger_hover;
    border-color: $danger_hover;
    color: #ffffff;
}
$_danger_pressed {
    background: $danger;
    border-color: $danger;
    color: #ffffff;
}

/* ---------------- inputs ---------------- */
QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit, QDateTimeEdit,
QTimeEdit, QDateEdit, QPlainTextEdit, QTextEdit {
    background-color: $input;
    border: 1px solid $border_strong;
    border-radius: 4px;
    padding: 2px 7px;
    selection-background-color: $accent;
    selection-color: #ffffff;
    color: $text;
}
QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit, QDateTimeEdit,
QTimeEdit, QDateEdit {
    min-height: 20px;
    max-height: 24px;
}
QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QLineEdit:focus,
QDateTimeEdit:focus, QTimeEdit:focus, QDateEdit:focus,
QPlainTextEdit:focus, QTextEdit:focus {
    border-color: $accent;
    background-color: $surface;
}
QComboBox:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled,
QLineEdit:disabled, QDateTimeEdit:disabled, QPlainTextEdit:disabled {
    color: $text_disabled;
    background-color: $disabled_bg;
    border-color: $border;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    border-left: 1px solid $border_strong;
    border-top-right-radius: 3px;
    border-bottom-right-radius: 3px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 $button_top, stop:1 $button_bottom);
    width: 24px;
}
QComboBox::down-arrow {
    width: 9px;
    height: 9px;
}
QComboBox QAbstractItemView {
    background-color: $surface;
    border: 1px solid $border;
    border-radius: 6px;
    padding: 4px;
    selection-background-color: $accent_soft;
    selection-color: $text;
    outline: none;
}
QSpinBox::up-button, QDoubleSpinBox::up-button, QDateTimeEdit::up-button,
QSpinBox::down-button, QDoubleSpinBox::down-button, QDateTimeEdit::down-button {
    subcontrol-origin: border;
    border-left: 1px solid $border_strong;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 $button_top, stop:1 $button_bottom);
    width: 20px;
}
QSpinBox::up-button, QDoubleSpinBox::up-button, QDateTimeEdit::up-button {
    subcontrol-position: top right;
    border-bottom: 1px solid $border;
    border-top-right-radius: 3px;
}
QSpinBox::down-button, QDoubleSpinBox::down-button, QDateTimeEdit::down-button {
    subcontrol-position: bottom right;
    border-bottom-right-radius: 3px;
}
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow, QDateTimeEdit::up-arrow,
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow, QDateTimeEdit::down-arrow {
    width: 8px;
    height: 6px;
}

/* ---------------- lists, trees, tables ---------------- */
QListView, QListWidget, QTreeView, QTableView, QTreeWidget {
    background-color: $surface;
    border: 1px solid $border;
    border-radius: 6px;
    alternate-background-color: $surface_alt;
    outline: none;
}
QListView::item, QListWidget::item, QTreeView::item, QTableView::item {
    padding: 4px 6px;
    border-radius: 0px;
}
QListView::item:selected, QListWidget::item:selected,
QTreeView::item:selected, QTableView::item:selected {
    background: $accent_soft;
    color: $text;
}
QListView::item:hover, QListWidget::item:hover,
QTreeView::item:hover, QTableView::item:hover {
    background: $surface_alt;
}
QHeaderView::section {
    background: $surface_alt;
    color: $text_secondary;
    padding: 5px 8px;
    border: none;
    border-bottom: 1px solid $border;
    font-weight: 600;
}

/* ---------------- scroll areas & bars ---------------- */
QScrollArea {
    border: none;
    background: transparent;
}
QScrollBar:horizontal {
    background: transparent;
    height: 12px;
    border-radius: 0px;
    margin: 0;
}
QScrollBar::handle:horizontal {
    background: $scroll_handle;
    border-radius: 6px;
    min-width: 32px;
}
QScrollBar::handle:horizontal:hover {
    background: $scroll_handle_hover;
}
QScrollBar:vertical {
    background: transparent;
    width: 12px;
    border-radius: 0px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: $scroll_handle;
    border-radius: 6px;
    min-height: 32px;
}
QScrollBar::handle:vertical:hover {
    background: $scroll_handle_hover;
}
QScrollBar::add-line, QScrollBar::sub-line {
    width: 0;
    height: 0;
}
QScrollBar::add-page, QScrollBar::sub-page {
    background: transparent;
}

/* ---------------- sidebar ---------------- */
#Sidebar, #SidebarScroll, #SidebarScroll > QWidget {
    background: $surface;
}
QToolButton#SidebarSectionHeader {
    background: transparent;
    border: none;
    border-bottom: 1px solid $border;
    border-radius: 0;
    text-align: left;
    padding: 7px 8px;
    font-weight: 600;
    font-size: 9pt;
    color: $text_secondary;
}
QToolButton#SidebarSectionHeader:hover {
    background: $accent_soft;
    color: $text;
}
QToolButton#SidebarSectionHeader:pressed {
    background: $accent_soft_2;
}
QToolButton#SidebarSectionHeader:checked {
    color: $accent;
}
QMainWindow::separator {
    background: $border;
    width: 1px;
    height: 1px;
}
QSplitter::handle {
    background: $border;
}

/* ---------------- groups & tabs ---------------- */
QGroupBox {
    border: 1px solid $border;
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 8px;
    background: transparent;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 6px;
    color: $accent;
    font-weight: 600;
}
QTabWidget::pane {
    border: 1px solid $border;
    border-radius: 8px;
    background: $surface;
    top: -1px;
}
QTabBar::tab {
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 6px 16px;
    color: $text_secondary;
    font-weight: 500;
}
QTabBar::tab:selected {
    color: $accent;
    border-bottom: 2px solid $accent;
    font-weight: 600;
}
QTabBar::tab:hover:!selected {
    color: $text;
}

/* ---------------- sliders ---------------- */
QSlider::groove:horizontal {
    height: 4px;
    background: $slider_groove;
    border-radius: 0px;
}
QSlider::sub-page:horizontal {
    background: $accent;
    border-radius: 0px;
}
QSlider::handle:horizontal {
    width: 14px;
    margin: -5px 0;
    border-radius: 0px;
    background: $surface;
    border: 2px solid $accent;
}
QSlider::handle:horizontal:hover {
    background: $accent;
}
QSlider::groove:vertical {
    width: 4px;
    background: $slider_groove;
    border-radius: 0px;
}
QSlider::sub-page:vertical {
    background: $accent;
    border-radius: 0px;
}
QSlider::handle:vertical {
    height: 14px;
    margin: 0 -5px;
    border-radius: 0px;
    background: $surface;
    border: 2px solid $accent;
}
QSlider::handle:vertical:hover {
    background: $accent;
}

/* ---------------- checkboxes & radios ---------------- */
QCheckBox, QRadioButton {
    spacing: 6px;
}
/* Keep QCheckBox native: Fusion draws a real check mark (✓).  Painting the
   whole checked indicator with QSS hides that glyph on Windows. */
QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid $border_strong;
    background: $surface;
}
QRadioButton::indicator {
    border-radius: 0px;
}
QRadioButton::indicator:hover {
    border-color: $accent;
}
QRadioButton::indicator:checked {
    background: $accent;
    border-color: $accent;
}
QRadioButton::indicator:disabled {
    border-color: $border;
    background: $disabled_bg;
}

/* ---------------- misc ---------------- */
QStatusBar {
    background: $surface;
    border-top: 1px solid $border;
}
QStatusBar::item {
    border: none;
}
QToolTip {
    background: $tooltip_bg;
    color: $tooltip_text;
    border: none;
    padding: 4px 8px;
    border-radius: 0px;
    font-size: 9pt;
}
QProgressBar {
    border: 1px solid $border;
    border-radius: 6px;
    text-align: center;
    background: $surface;
    color: $text;
}
QProgressBar::chunk {
    background: $accent;
    border-radius: 5px;
}

/* ---------------- calendar popup ---------------- */
QCalendarWidget QWidget#qt_calendar_navigationbar {
    background: $surface_alt;
}
QCalendarWidget QToolButton {
    background: transparent;
    border: none;
    border-radius: 0px;
    padding: 2px 6px;
    color: $text;
}
QCalendarWidget QToolButton:hover {
    background: $accent_soft;
}
QCalendarWidget QAbstractItemView {
    background: $surface;
    color: $text;
    selection-background-color: $accent;
    selection-color: #ffffff;
    outline: none;
}
QCalendarWidget QSpinBox {
    background: $input;
}
""")


def build_stylesheet(theme_name: str = "light", tone_name: str = "black") -> str:
    """Return the Qt stylesheet for the given theme name."""
    theme_name = theme_name if theme_name in THEMES else "light"
    palette = resolved_theme(theme_name, tone_name)
    palette["_primary"] = _PRIMARY_SELECTOR
    palette["_primary_hover"] = _state_selector(_PRIMARY_BUTTONS, "hover")
    palette["_primary_pressed"] = _state_selector(_PRIMARY_BUTTONS, "pressed")
    palette["_primary_disabled"] = _state_selector(_PRIMARY_BUTTONS, "disabled")
    palette["_danger"] = _DANGER_SELECTOR
    palette["_danger_hover"] = _state_selector(_DANGER_BUTTONS, "hover")
    palette["_danger_pressed"] = _state_selector(_DANGER_BUTTONS, "pressed")
    return _STYLESHEET_TEMPLATE.substitute(palette)


# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------

def _setup_app_font(app: QApplication) -> None:
    """Set a per-platform font family so text scales with the display DPI."""
    font = QFont()
    font.setFamilies(font_families())
    font.setPointSizeF(9.5)
    app.setFont(font)


# ---------------------------------------------------------------------------
# Matplotlib theming
# ---------------------------------------------------------------------------

_MPL_SHARED = {
    "figure.dpi": 100,
    "savefig.dpi": 200,
    "font.size": 9.0,
    "axes.titlesize": 10.0,
    "axes.labelsize": 9.0,
    "xtick.labelsize": 8.0,
    "ytick.labelsize": 8.0,
    "legend.fontsize": 8.5,
    "axes.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "lines.linewidth": 1.0,
    "grid.linewidth": 0.8,
    "image.cmap": "jet",
}


def build_palette(theme_name: str = "light", tone_name: str = "black"):
    """Return a QPalette matching the theme.

    The stylesheet covers most widgets, but a few things are drawn by the
    style itself (combo/spin arrows, check indicators in menus, separators,
    the calendar popup, ...) and pick their colors from the palette - so
    both themes need a consistent palette or those elements stay light (and
    nearly invisible) in dark mode.
    """
    from PySide6.QtGui import QPalette
    from PySide6.QtGui import QColor

    theme_name = theme_name if theme_name in THEMES else "light"
    p = resolved_theme(theme_name, tone_name)

    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window, QColor(p["window"]))
    pal.setColor(QPalette.ColorRole.WindowText, QColor(p["text"]))
    pal.setColor(QPalette.ColorRole.Base, QColor(p["input"]))
    pal.setColor(QPalette.ColorRole.AlternateBase, QColor(p["surface_alt"]))
    pal.setColor(QPalette.ColorRole.ToolTipBase, QColor(p["tooltip_bg"]))
    pal.setColor(QPalette.ColorRole.ToolTipText, QColor(p["tooltip_text"]))
    pal.setColor(QPalette.ColorRole.Text, QColor(p["text"]))
    pal.setColor(QPalette.ColorRole.PlaceholderText, QColor(p["text_disabled"]))
    pal.setColor(QPalette.ColorRole.Button, QColor(p["surface"]))
    pal.setColor(QPalette.ColorRole.ButtonText, QColor(p["text"]))
    pal.setColor(QPalette.ColorRole.BrightText, QColor("#ffffff"))
    pal.setColor(QPalette.ColorRole.Highlight, QColor(p["accent"]))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    pal.setColor(QPalette.ColorRole.Link, QColor(p["accent"]))
    pal.setColor(QPalette.ColorRole.Mid, QColor(p["border"]))
    pal.setColor(QPalette.ColorRole.Midlight, QColor(p["border"]))
    pal.setColor(QPalette.ColorRole.Dark, QColor(p["border_strong"]))
    pal.setColor(QPalette.ColorRole.Shadow, QColor(p["border_strong"]))
    pal.setColor(QPalette.ColorRole.Light, QColor(p["surface"]))

    disabled = QPalette.ColorGroup.Disabled
    pal.setColor(disabled, QPalette.ColorRole.WindowText, QColor(p["text_disabled"]))
    pal.setColor(disabled, QPalette.ColorRole.Text, QColor(p["text_disabled"]))
    pal.setColor(disabled, QPalette.ColorRole.ButtonText, QColor(p["text_disabled"]))
    pal.setColor(disabled, QPalette.ColorRole.Base, QColor(p["disabled_bg"]))
    pal.setColor(disabled, QPalette.ColorRole.Button, QColor(p["disabled_bg"]))
    return pal


def apply_matplotlib_theme(theme_name: str = "light", tone_name: str = "black") -> None:
    """Apply the theme colors to the matplotlib defaults (affects new figures)."""
    import matplotlib as mpl
    from matplotlib import font_manager

    theme_name = theme_name if theme_name in THEMES else "light"
    mpl.rcParams.update(_MPL_SHARED)
    # Use the first font family that is actually installed, so matplotlib
    # does not warn about every missing CJK fallback on each text draw.
    for family in font_families():
        try:
            font_manager.findfont(family, fallback_to_default=False)
            mpl.rcParams["font.family"] = family
            break
        except Exception:
            continue
    mpl.rcParams.update(resolved_theme(theme_name, tone_name)["mpl"])


def retheme_figures(theme_name: str = "light", tone_name: str = "black") -> None:
    """Restyle every currently open matplotlib figure for ``theme_name``.

    Used after a live theme toggle so existing canvases (signal area,
    hypnogram, spectrum window, ...) follow the new colors without
    recreating them.
    """
    import matplotlib.pyplot as plt

    theme_name = theme_name if theme_name in THEMES else "light"
    mpl_colors = resolved_theme(theme_name, tone_name)["mpl"]
    for num in plt.get_fignums():
        fig = plt.figure(num)
        try:
            fig.patch.set_facecolor(mpl_colors["figure.facecolor"])
            for ax in fig.axes:
                ax.set_facecolor(mpl_colors["axes.facecolor"])
                for spine in ax.spines.values():
                    spine.set_edgecolor(mpl_colors["axes.edgecolor"])
                ax.tick_params(colors=mpl_colors["xtick.color"], which="both")
                if ax.xaxis.label is not None:
                    ax.xaxis.label.set_color(mpl_colors["axes.labelcolor"])
                if ax.yaxis.label is not None:
                    ax.yaxis.label.set_color(mpl_colors["axes.labelcolor"])
            fig.canvas.draw_idle()
        except Exception:  # pragma: no cover - a figure may be mid-close
            continue


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def apply_theme(app: QApplication, theme_name: str = "light",
                tone_name: str = "black") -> str:
    """Apply a full MiSleep theme (style + fonts + matplotlib) to ``app``.

    Parameters
    ----------
    app : QApplication
        The application to style.
    theme_name : str
        ``"light"`` or ``"dark"``. Unknown names fall back to ``"light"``.

    Returns
    -------
    str
        The theme name that was actually applied.
    """
    theme_name = theme_name if theme_name in THEMES else "light"

    # Fusion renders identically on every platform, so the QSS look is
    # predictable on Windows / Linux. On macOS, switching the style at
    # runtime crashes Qt with a Bus error (known PySide6/Qt bug on macOS,
    # especially arm64), so the native style is kept there - the stylesheet
    # still applies on top of it.
    if sys.platform != "darwin":
        try:
            app.setStyle("Fusion")
        except Exception:  # pragma: no cover
            pass

    _setup_app_font(app)
    app.setPalette(build_palette(theme_name, tone_name))
    app.setStyleSheet(build_stylesheet(theme_name, tone_name))
    apply_matplotlib_theme(theme_name, tone_name)
    return theme_name


def apply_app_style(app: QApplication) -> None:
    """Backward-compatible alias: apply the default (light) theme."""
    apply_theme(app, "light")
