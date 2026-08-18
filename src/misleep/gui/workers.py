# -*- coding: UTF-8 -*-
"""Background worker threads for the GUI.

These QThread subclasses keep file I/O off the UI thread so the interface
stays responsive while saving large files.
"""

from PySide6.QtCore import QThread

from misleep.io.annotation import save_misleep_anno
from misleep.io.base import write_signal
from misleep.io.mat import load_mat


class SaveThread(QThread):
    """Save files (annotation, data, configuration) in a background thread.

    Parameters
    ----------
    parent : QObject, optional
    file : ANY, optional
        Object to save: a ``[mianno, midata]`` pair for annotations, a
        ``MiData`` for data, or a ConfigParser for configuration.
    file_path : str, optional
        Destination path.
    """

    def __init__(self, parent=None, file=None, file_path=None):
        super().__init__(parent)
        self.file = file
        self.file_path = file_path

    def save_config(self):
        """Save a ConfigParser to ``self.file_path``."""
        with open(self.file_path, "w", encoding="utf-8") as config_file:
            self.file.write(config_file)

    def save_anno(self):
        """Save an annotation; ``self.file`` must be ``[mianno, midata]``."""
        mianno, midata = self.file
        return save_misleep_anno(mianno, midata, self.file_path)

    def save_data(self):
        """Save a :class:`MiData` through the registered format writer."""
        midata = self.file
        if midata is None:
            return False

        write_signal(midata, self.file_path)
        return True


class LoadThread(QThread):
    """Load data in a background thread.

    Parameters
    ----------
    parent : QObject, optional
    file_path : str, optional
        File to load.
    """

    def __init__(self, parent=None, file_path=None):
        super().__init__(parent)
        self.file_path = file_path

    def load_mat_data(self):
        """Load data from a ``.mat`` file."""
        return load_mat(data_path=self.file_path)
