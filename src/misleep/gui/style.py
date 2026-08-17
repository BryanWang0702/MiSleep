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
        "window": "#eaeef5",
        "surface": "#ffffff",
        "surface_alt": "#e2e8f2",
        "input": "#ffffff",
        "disabled_bg": "#eef1f6",
        # lines
        "border": "#c9d3e1",
        "border_strong": "#a9b6c9",
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
            "figure.facecolor": "#eaeef5",
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
        "border_strong": "#414e68",
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
    background: transparent;
    border: 1px solid transparent;
    border-radius: 0px;
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
    border-radius: 0px;
    padding: 4px 12px;
    color: $text;
    min-height: 26px;
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

/* the small 24x24 channel-move arrows keep their compact size */
#MoveUpBt, #MoveDownBt {
    min-height: 24px;
    max-height: 24px;
    min-width: 24px;
    max-width: 24px;
    padding: 0px;
    font-size: 10pt;
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
    border-radius: 0px;
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
    border-radius: 0px;
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
    border-radius: 0px;
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
    border-radius: 0px;
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
    border-radius: 0px;
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
    border-radius: 0px;
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
    border-radius: 0px;
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
QCheckBox::indicator, QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid $border_strong;
    background: $surface;
}
QCheckBox::indicator {
    border-radius: 0px;
}
QRadioButton::indicator {
    border-radius: 0px;
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
    border-radius: 0px;
    font-size: 9pt;
}
QProgressBar {
    border: 1px solid $border;
    border-radius: 0px;
    text-align: center;
    background: $surface;
    color: $text;
}
QProgressBar::chunk {
    background: $accent;
    border-radius: 0px;
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
    "image.cmap": "jet",
}


def build_palette(theme_name: str = "light"):
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
    p = THEMES[theme_name]

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
    app.setPalette(build_palette(theme_name))
    app.setStyleSheet(build_stylesheet(theme_name))
    apply_matplotlib_theme(theme_name)
    return theme_name


def apply_app_style(app: QApplication) -> None:
    """Backward-compatible alias: apply the default (light) theme."""
    apply_theme(app, "light")
