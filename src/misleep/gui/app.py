# -*- coding: UTF-8 -*-
"""Application entry point for the MiSleep GUI.

Sets up the Qt/PySide6 environment (including the ``QT_API`` variable
needed by matplotlib) and starts the main window.

Files can be opened directly from the command line::

    misleep                          # empty session
    misleep data.mat                 # load data on startup
    misleep data.mat anno.txt        # load data + annotation on startup
    misleep --data data.edf --anno anno.txt
    python -m misleep data.mat anno.txt

On Windows, after running ``tools/install_file_associations.py``,
double-clicking a registered ``.mat`` / ``.edf`` file opens it in MiSleep
automatically.
"""

import argparse
import os
import sys

# Make matplotlib use the PySide6 Qt bindings before anything imports it.
os.environ.setdefault("QT_API", "pyside6")

from misleep.gui import resources  # noqa: F401  (register Qt resources)
from misleep.gui.qt_utils import app_icon
from misleep.logger import logger


def _setup_high_dpi():
    """Configure Qt high-DPI behaviour before the QApplication is created.

    Qt6 enables high-DPI scaling by default and manages its own
    per-monitor DPI awareness context; this additionally uses
    *pass-through* scale-factor rounding so fractional display scales
    (e.g. 125 % / 150 % on 2K screens) are applied exactly instead of
    being rounded to 0.5 steps.
    """
    try:
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QGuiApplication

        QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    except Exception:  # pragma: no cover
        pass

    # Note: do NOT call SetProcessDpiAwareness/SetProcessDPIAware here -
    # Qt6 already sets DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2, and a
    # second explicit call fails with "Access is denied" (the awareness can
    # only be set once per process).

    if sys.platform == "win32":
        # Give this process an explicit AppUserModelID so the Windows
        # taskbar shows the MiSleep window icon instead of the generic
        # python.exe logo. Must be set before the first window is shown.
        try:
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "BryanWang0702.MiSleep")
        except Exception:  # pragma: no cover
            pass


def _parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="misleep",
        description="MiSleep: mice sleep EEG/EMG visualization, scoring and analysis.",
    )
    parser.add_argument(
        "files", nargs="*", metavar="FILE",
        help="Optional signal file (.mat/.edf) and, optionally, annotation file "
             "(.txt). e.g. `misleep data.mat anno.txt`")
    parser.add_argument(
        "--data", dest="data_path", default=None, metavar="PATH",
        help="Signal file (.mat/.edf) to open on startup.")
    parser.add_argument(
        "--anno", dest="anno_path", default=None, metavar="PATH",
        help="Annotation file (.txt) to open on startup.")
    parser.add_argument(
        "--version", action="version",
        version=f"%(prog)s {_version()}",
    )
    args = parser.parse_args(argv)

    # positional files: first = data, second = annotation.
    # When --data is already given, a single positional file is the annotation.
    data_path = args.data_path
    anno_path = args.anno_path
    if args.files:
        if data_path is None:
            data_path = args.files[0]
            if len(args.files) > 1:
                anno_path = anno_path or args.files[1]
        else:
            anno_path = anno_path or args.files[0]
    return data_path, anno_path


def _version():
    from misleep import __version__

    return __version__


def _prewarm():
    """Pay the one-time warm-up costs (font cache, heavy scipy imports)
    in the background so the window appears instantly.

    Without this, the very first plot after loading a file silently pays
    ~1-2 s of matplotlib font-cache building and scipy imports, which the
    user perceives as a slow "initialize/draw" phase.  Running it in a
    daemon thread keeps the UI responsive; if a file is loaded before the
    warm-up finishes, the import lock simply blocks until it completes.
    """
    try:
        import scipy.integrate  # noqa: F401
        import scipy.ndimage  # noqa: F401
        import scipy.signal  # noqa: F401

        from matplotlib import font_manager
        font_manager.findfont("DejaVu Sans")  # build / load the font cache

        import matplotlib.pyplot as plt
        plt.get_cmap("jet")

        from misleep.preprocessing import spectral  # noqa: F401
        from misleep.viz import spectral as _viz_spectral  # noqa: F401
    except Exception:  # pragma: no cover
        pass


def show(data_path=None, anno_path=None):
    """Create and show the MiSleep main window (blocking).

    Parameters
    ----------
    data_path : str, optional
        Signal file (``.mat`` / ``.edf``) to open on startup.
    anno_path : str, optional
        Annotation file (``.txt``) to open on startup.
    """
    try:
        from PySide6.QtWidgets import QApplication
    except ImportError as e:  # pragma: no cover
        raise ImportError(
            "The MiSleep GUI requires PySide6. Install it with: "
            "pip install 'misleep[gui]'  (or: pip install PySide6)"
        ) from e

    _setup_high_dpi()

    # Imported after the Qt bindings are resolved by matplotlib.
    from misleep.gui.main_window import MainWindow

    app = QApplication.instance() or QApplication(sys.argv[:1])
    app.setApplicationName("MiSleep")
    app.setApplicationDisplayName("MiSleep")
    app.setWindowIcon(app_icon())

    # Warm-up one-time costs in a background thread so the window appears
    # immediately and the first file load renders fast.
    import threading

    threading.Thread(target=_prewarm, daemon=True).start()

    main_win = MainWindow()

    if data_path:
        logger.info("Opening data file: %s", data_path)
        main_win.open_data(data_path)
    if anno_path:
        logger.info("Opening annotation file: %s", anno_path)
        main_win.open_annotation(anno_path)

    main_win.showMaximized()  # start maximized: no horizontal scrolling
    sys.exit(app.exec())


def main(argv=None):
    """Console-script entry point (``misleep``)."""
    data_path, anno_path = _parse_args(argv)
    show(data_path=data_path, anno_path=anno_path)


if __name__ == "__main__":
    main()
