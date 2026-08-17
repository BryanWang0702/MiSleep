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
        "window": "#eef1f7",
        "surface": "#ffffff",
        "surface_alt": "#e8edf5",
        "input": "#ffffff",
        "disabled_bg": "#f0f3f8",
        # lines
        "border": "#d5dcea",
        "border_strong": "#b9c4d6",
        # text
        "text": "#1c2736",
        "text_secondary": "#5a6a7e",
        "text_disabled": "#a3aebb",
        # accent
        "accent": "#2f6bff",
        "accent_hover": "#2258e6",
        "accent_pressed": "#1a49c4",
        "accent_soft": "#e3ebff",
        "accent_soft_2": "#d3e0fb",
        # semantic
        "danger": "#e5484d",
        "danger_hover": "#d23b40",
        "success": "#17a673",
        # misc
        "tooltip_bg": "#223042",
        "tooltip_text": "#f2f5fa",
        "scroll_handle": "#b9c4d6",
        "scroll_handle_hover": "#8fa0b8",
        "slider_groove": "#d5dcea",
        # matplotlib / plot area
        "plot": {"trace": "#0e1520", "grid": "#37a57f", "bg": "#ffffff"},
        "mpl": {
            "figure.facecolor": "#eef1f7",
            "axes.facecolor": "#ffffff",
            "axes.edgecolor": "#b9c4d6",
            "axes.labelcolor": "#1c2736",
            "xtick.color": "#5a6a7e",
            "ytick.color": "#5a6a7e",
            "text.color": "#1c2736",
            "grid.color": "#dfe5ee",
            "savefig.facecolor": "#ffffff",
        },
    },
    "dark": {
        "name": "Dark",
        # surfaces
        "window": "#131a24",
        "surface": "#1a2330",
        "surface_alt": "#212c3c",
        "input": "#161f2b",
        "disabled_bg": "#1a2330",
        # lines
        "border": "#2a3648",
        "border_strong": "#3b4a63",
        # text
        "text": "#e7edf6",
        "text_secondary": "#9aa8bb",
        "text_disabled": "#5d6c80",
        # accent
        "accent": "#4d8dff",
        "accent_hover": "#6ba1ff",
        "accent_pressed": "#3a74e6",
        "accent_soft": "#24395e",
        "accent_soft_2": "#2c4470",
        # semantic
        "danger": "#f0606b",
        "danger_hover": "#f27c85",
        "success": "#2bc48a",
        # misc
        "tooltip_bg": "#2b3648",
        "tooltip_text": "#e7edf6",
        "scroll_handle": "#3b4a63",
        "scroll_handle_hover": "#55698a",
        "slider_groove": "#2a3648",
        # matplotlib / plot area
        "plot": {"trace": "#d9e3f2", "grid": "#3fae85", "bg": "#101824"},
        "mpl": {
            "figure.facecolor": "#131a24",
            "axes.facecolor": "#101824",
            "axes.edgecolor": "#3b4a63",
            "axes.labelcolor": "#e7edf6",
            "xtick.color": "#9aa8bb",
            "ytick.color": "#9aa8bb",
            "text.color": "#e7edf6",
            "grid.color": "#232f41",
            "savefig.facecolor": "#101824",
        },
    },
}

#: Buttons that act as *primary* actions get the accent colour.
_PRIMARY_BUTTONS = (
    "SaveLabelBt", "FilterConfirmBt", "MultipleScalerConfirmBt",
    "PlotSpecBt", "LabelBt",
)

#: Buttons that destroy things get the danger colour.
_DANGER_BUTTONS = ("DeleteChBt",)

_PRIMARY_SELECTOR = ", ".join(f"#{name}" for name in _PRIMARY_BUTTONS)
_DANGER_SELECTOR = ", ".join(f"#{name}" for name in _DANGER_BUTTONS)


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
    border-radius: 6px;
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
    border-radius: 8px;
    padding: 5px;
}
QMenu::item {
    padding: 5px 26px 5px 10px;
    border-radius: 5px;
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
    background: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 4px 8px;
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
    background-color: $surface;
    border: 1px solid $border_strong;
    border-radius: 6px;
    padding: 4px 12px;
    color: $text;
}
QPushButton:hover {
    background-color: $surface_alt;
    border-color: $accent;
}
QPushButton:pressed {
    background-color: $accent_soft_2;
}
QPushButton:focus {
    border-color: $accent;
}
QPushButton:disabled {
    color: $text_disabled;
    background-color: $disabled_bg;
    border-color: $border;
}
QPushButton:checked {
    background-color: $accent_soft;
    border-color: $accent;
    color: $accent;
}
QPushButton[default="true"] {
    background-color: $accent;
    border-color: $accent;
    color: #ffffff;
}
QPushButton[default="true"]:hover {
    background-color: $accent_hover;
    border-color: $accent_hover;
}
QPushButton[default="true"]:pressed {
    background-color: $accent_pressed;
    border-color: $accent_pressed;
}

/* primary actions */
$_primary {
    background-color: $accent;
    border-color: $accent;
    color: #ffffff;
    font-weight: 600;
}
$_primary:hover {
    background-color: $accent_hover;
    border-color: $accent_hover;
}
$_primary:pressed {
    background-color: $accent_pressed;
    border-color: $accent_pressed;
}
$_primary:disabled {
    background-color: $disabled_bg;
    border-color: $border;
    color: $text_disabled;
    font-weight: 400;
}

/* destructive actions */
$_danger {
    background-color: $surface;
    border-color: $danger;
    color: $danger;
}
$_danger:hover {
    background-color: $danger_hover;
    border-color: $danger_hover;
    color: #ffffff;
}
$_danger:pressed {
    background-color: $danger;
    border-color: $danger;
    color: #ffffff;
}

/* ---------------- inputs ---------------- */
QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit, QDateTimeEdit,
QTimeEdit, QDateEdit, QPlainTextEdit, QTextEdit {
    background-color: $input;
    border: 1px solid $border_strong;
    border-radius: 6px;
    padding: 3px 8px;
    selection-background-color: $accent;
    selection-color: #ffffff;
    color: $text;
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
    border: none;
    width: 22px;
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
    border: none;
    background: transparent;
    width: 18px;
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
    border-radius: 4px;
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
    border-radius: 6px;
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
    border-radius: 6px;
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

/* ---------------- docks ---------------- */
QDockWidget {
    color: $text;
    font-weight: 600;
    font-size: 9pt;
}
QDockWidget::title {
    background: $surface;
    border-bottom: 1px solid $border;
    padding: 5px 8px;
    text-align: left;
}
QDockWidget > QWidget {
    background: $window;
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
    border-radius: 6px;
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
    border-radius: 2px;
}
QSlider::sub-page:horizontal {
    background: $accent;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    width: 14px;
    margin: -5px 0;
    border-radius: 7px;
    background: $surface;
    border: 2px solid $accent;
}
QSlider::handle:horizontal:hover {
    background: $accent;
}
QSlider::groove:vertical {
    width: 4px;
    background: $slider_groove;
    border-radius: 2px;
}
QSlider::sub-page:vertical {
    background: $accent;
    border-radius: 2px;
}
QSlider::handle:vertical {
    height: 14px;
    margin: 0 -5px;
    border-radius: 7px;
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
QCheckBox::indicator, QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid $border_strong;
    background: $surface;
}
QCheckBox::indicator {
    border-radius: 4px;
}
QRadioButton::indicator {
    border-radius: 8px;
}
QCheckBox::indicator:hover, QRadioButton::indicator:hover {
    border-color: $accent;
}
QCheckBox::indicator:checked {
    background: $accent;
    border-color: $accent;
}
QRadioButton::indicator:checked {
    background: $accent;
    border-color: $accent;
}
QCheckBox::indicator:disabled, QRadioButton::indicator:disabled {
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
    border-radius: 4px;
    font-size: 9pt;
}
QProgressBar {
    border: 1px solid $border;
    border-radius: 5px;
    text-align: center;
    background: $surface;
    color: $text;
}
QProgressBar::chunk {
    background: $accent;
    border-radius: 4px;
}

/* small icon-ish toggle used in dock title bars */
#MetaToggleBt {
    border: none;
    background: transparent;
    padding: 2px 6px;
    font-size: 9pt;
    font-weight: 400;
}
#MetaToggleBt:hover {
    background: $accent_soft;
    border-radius: 4px;
}
""")


def build_stylesheet(theme_name: str = "light") -> str:
    """Return the Qt stylesheet for the given theme name."""
    theme_name = theme_name if theme_name in THEMES else "light"
    palette = dict(THEMES[theme_name])
    palette["_primary"] = _PRIMARY_SELECTOR
    palette["_danger"] = _DANGER_SELECTOR
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
    "image.cmap": "turbo",
}


def apply_matplotlib_theme(theme_name: str = "light") -> None:
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
    mpl.rcParams.update(THEMES[theme_name]["mpl"])


def retheme_figures(theme_name: str = "light") -> None:
    """Restyle every currently open matplotlib figure for ``theme_name``.

    Used after a live theme toggle so existing canvases (signal area,
    hypnogram, spectrum window, ...) follow the new colors without
    recreating them.
    """
    import matplotlib.pyplot as plt

    theme_name = theme_name if theme_name in THEMES else "light"
    mpl_colors = THEMES[theme_name]["mpl"]
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

def apply_theme(app: QApplication, theme_name: str = "light") -> str:
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
    # predictable across Windows / macOS / Linux (native styles would
    # override parts of the stylesheet).
    try:
        app.setStyle("Fusion")
    except Exception:  # pragma: no cover
        pass

    _setup_app_font(app)
    app.setStyleSheet(build_stylesheet(theme_name))
    apply_matplotlib_theme(theme_name)
    return theme_name


def apply_app_style(app: QApplication) -> None:
    """Backward-compatible alias: apply the default (light) theme."""
    apply_theme(app, "light")
