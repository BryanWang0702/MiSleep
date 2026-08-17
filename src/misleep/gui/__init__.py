# -*- coding: UTF-8 -*-
"""PySide6 graphical user interface for MiSleep.

Launch the GUI with::

    python -m misleep

or from Python::

    from misleep.gui import show
    show()

The GUI is built on **PySide6** (Qt6), which works on Windows, macOS and
Linux. Before importing anything from this module, make sure PySide6 is
installed (``pip install 'misleep[gui]'``) and that the ``QT_API``
environment variable is set to ``pyside6`` for matplotlib integration
(handled automatically by :mod:`misleep.gui.app`).
"""

from misleep.gui import resources as _resources  # noqa: F401  (register Qt resources)
from .app import main, show

__all__ = ["main", "show"]
