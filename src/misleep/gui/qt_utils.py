# -*- coding: UTF-8 -*-
"""GUI utility functions and Qt helper classes.

Pure helpers that the GUI uses for drawing spectra and formatting time;
the general-purpose helpers are re-exported from :mod:`misleep.utils` so
there is a single source of truth.
"""

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


def app_icon() -> QIcon:
    """Return the MiSleep application icon from the Qt resources.

    The square ``misleep.ico`` is the primary icon (crisp at small title-bar
    / taskbar sizes); ``logo.png`` is kept as the large-size fallback.
    """
    icon = QIcon()
    icon.addFile(":/logo/misleep.ico")
    icon.addFile(":/logo/logo.png")
    if icon.isNull():
        icon = QIcon(":/logo/logo.png")
    return icon


class CollapsibleSection(QWidget):
    """A titled, collapsible panel used in the right-hand sidebar.

    One header row with a fold/unfold arrow plus a content widget that can
    be hidden. Replaces the old draggable docks with a tidy, fixed panel.
    """

    def __init__(self, title, content=None, parent=None, collapsed=False):
        super().__init__(parent)
        self._title = title
        self._content = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.header = QToolButton()
        self.header.setObjectName("SidebarSectionHeader")
        self.header.setCheckable(True)
        self.header.setChecked(not collapsed)
        self.header.setCursor(Qt.CursorShape.PointingHandCursor)
        self.header.setSizePolicy(QSizePolicy.Policy.Expanding,
                                  QSizePolicy.Policy.Fixed)
        self.header.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.header.setToolTip("Click to expand / collapse")
        self.header.clicked.connect(self._on_header_clicked)
        layout.addWidget(self.header)

        if content is not None:
            self.set_content(content, collapsed=collapsed)
        self._update_arrow()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def set_content(self, widget, collapsed=None):
        """Attach the content widget (re-parents it into this section)."""
        if self._content is not None:
            self._content.setParent(None)
        self._content = widget
        if widget is not None:
            # Dock contents often retain a large layout size hint from their
            # former floating-dock geometry.  Ignore that horizontal hint so
            # the unified sidebar can actually constrain every section to its
            # viewport instead of silently clipping the rightmost controls.
            widget.setMinimumWidth(0)
            widget.setSizePolicy(QSizePolicy.Policy.Ignored,
                                 QSizePolicy.Policy.Preferred)
            self.layout().addWidget(widget)
            if collapsed is not None:
                self.header.setChecked(not collapsed)
                widget.setVisible(not collapsed)
        self._update_arrow()

    def set_expanded(self, expanded):
        """Programmatically expand (True) or collapse (False) the section."""
        self.header.setChecked(expanded)
        if self._content is not None:
            self._content.setVisible(expanded)
        self._update_arrow()

    def is_expanded(self):
        return self.header.isChecked()

    @property
    def title(self):
        return self._title

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _on_header_clicked(self):
        if self._content is not None:
            self._content.setVisible(self.header.isChecked())
        self._update_arrow()

    def _update_arrow(self):
        self.header.setArrowType(
            Qt.ArrowType.DownArrow if self.header.isChecked()
            else Qt.ArrowType.RightArrow)
        self.header.setText(self._title)


class ChannelListModel(QAbstractListModel):
    """A simple editable, drag-reorderable string list model.

    Unlike ``QStringListModel`` this implements ``moveRows``, so a
    drag & drop emits ``rowsMoved`` (a genuine move) instead of being
    performed as remove+insert -- which previously confused the rename
    logic.
    """

    def __init__(self, channels=None, parent=None):
        super().__init__(parent)
        self._channels = list(channels or [])

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._channels)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._channels)):
            return None
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            return self._channels[index.row()]
        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if role == Qt.ItemDataRole.EditRole and index.isValid() \
                and 0 <= index.row() < len(self._channels):
            self._channels[index.row()] = str(value)
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.EditRole])
            return True
        return False

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.ItemIsDropEnabled
        return (Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsDragEnabled)

    def moveRows(self, sourceParent, sourceRow, count, destinationParent, destinationChild):
        """Move a single row within the same list (drag & drop reorder)."""
        if sourceParent.isValid() or destinationParent.isValid():
            return False
        if count != 1 or sourceRow == destinationChild:
            return False
        if not (0 <= sourceRow < len(self._channels)):
            return False

        dest = destinationChild
        if sourceRow < dest:
            dest -= 1
        if dest < 0:
            dest = 0
        dest = min(dest, len(self._channels) - 1)

        last = sourceRow
        self.beginMoveRows(sourceParent, sourceRow, sourceRow, destinationParent, destinationChild)
        item = self._channels.pop(sourceRow)
        self._channels.insert(dest, item)
        self.endMoveRows()
        return True

    def channels(self):
        """Return a copy of the channel names in their current order."""
        return list(self._channels)

    def setChannels(self, channels):
        """Replace the whole list (no move/insert signals)."""
        self.beginResetModel()
        self._channels = list(channels)
        self.endResetModel()


def cal_draw_spectrum(data, sf, nperseg, freq_band=None, relative=None, nfft=None, gaussian_sigma=None):
    """Calculate a power spectrum and return it together with a figure.

    Parameters
    ----------
    data : ndarray
        Signal to analyze.
    sf : float
        Sampling frequency.
    nperseg : int
        Window length (in samples) for the Welch FFT.
    freq_band : list, optional
        Frequency band ``[low, high]``. Defaults to ``[0.5, 30]``.
    relative : bool, optional
        Whether to normalize the PSD to a relative power.
    nfft : int, optional
        Number of FFT points.
    gaussian_sigma : float, optional
        Gaussian smoothing sigma.

    Returns
    -------
    (spectrum, figure) : tuple
        ``spectrum`` is an array of shape ``(2, n_freq)`` (frequencies and
        powers); ``figure`` is the matplotlib figure.
    """
    # IMPORTANT: build the figure with matplotlib.figure.Figure directly
    # (not pyplot).  The old ``plt.close()`` here silently closed the main
    # window's figures, which froze the signal/hypnogram panels after an
    # export.  A non-pyplot figure is invisible to pyplot bookkeeping.
    import numpy as np
    from matplotlib.figure import Figure
    from scipy.ndimage import gaussian_filter1d
    from scipy.signal import welch

    if freq_band is None:
        freq_band = [0.5, 30]
    F, P = welch(data, sf, nperseg=nperseg, nfft=nfft, scaling="density")

    F = np.array([round(each, 2) for each in F])
    if gaussian_sigma is not None:
        P = gaussian_filter1d(P, sigma=gaussian_sigma)

    if freq_band is not None:
        idx_band = np.logical_and(F >= freq_band[0], F <= freq_band[1])
        F = F[idx_band]
        P = P[idx_band]

    if relative:
        total = sum(P)
        if total > 0:
            P = [each / total for each in P]

    major_ticks_top = np.linspace(0, freq_band[1] + 0.1, 10)

    figure = Figure(figsize=(10, 7))
    ax = figure.subplots(nrows=1, ncols=1)
    figure.subplots_adjust(top=0.95, left=0.15, bottom=0.15, right=0.95)

    ax.xaxis.set_ticks(major_ticks_top)
    ax.grid(which="major", alpha=0.6)

    ax.set_xlim(freq_band[0], freq_band[1] + 0.1)
    ax.plot(F, P)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Power spectral density (Power/Hz)")

    return np.array([F, P]), figure


# Re-export shared helpers so existing imports of ``misleep.gui.utils`` keep working.
from misleep.utils.misc import (  # noqa: E402, F401
    create_new_mianno,
    identify_startend_color,
    get_base_path,
    downsample_by_most_frequent,
)
from misleep.utils.time_utils import second2time, transfer_time  # noqa: E402, F401
from misleep.utils.annotation import insert_row, temp_loop4below_row  # noqa: E402, F401

__all__ = [
    "cal_draw_spectrum",
    "create_new_mianno",
    "identify_startend_color",
    "get_base_path",
    "downsample_by_most_frequent",
    "second2time",
    "transfer_time",
    "insert_row",
    "temp_loop4below_row",
]
