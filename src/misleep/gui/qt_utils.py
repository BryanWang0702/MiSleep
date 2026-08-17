# -*- coding: UTF-8 -*-
"""GUI utility functions and Qt helper classes.

Pure helpers that the GUI uses for drawing spectra and formatting time;
the general-purpose helpers are re-exported from :mod:`misleep.utils` so
there is a single source of truth.
"""

import numpy as np
from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt
from PySide6.QtGui import QIcon
from scipy.ndimage import gaussian_filter1d
from scipy.signal import welch


def app_icon() -> QIcon:
    """Return the MiSleep application icon from the Qt resources."""
    return QIcon(":/logo/logo.png")


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
    import matplotlib.pyplot as plt

    plt.close()

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

    figure = plt.figure(figsize=(10, 7))
    ax = figure.subplots(nrows=1, ncols=1)
    plt.subplots_adjust(top=0.95, left=0.15, bottom=0.15, right=0.95)

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
