# -*- coding: UTF-8 -*-
"""Render the MiSleep GUI offscreen to PNG previews (light & dark themes).

Development / documentation helper -- it renders the main window (with the
bundled example data and a synthetic annotation) and the settings dialog in
both themes, and saves the screenshots under ``docs/imgs/gui/``.

Usage::

    python tools/render_gui_preview.py

The user configuration is redirected into a temp folder, so running this
script never touches your real ``~/.misleep`` settings.
"""

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_API", "pyside6")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

# Isolate the user config so the preview never modifies the real one.
import shutil  # noqa: E402

import misleep.config as _config_module  # noqa: E402
import misleep.logger as _logger_module  # noqa: E402

_PREVIEW_CONFIG_DIR = ROOT / ".tmp" / "gui_preview_config"


def _fake_data_dir():
    return _PREVIEW_CONFIG_DIR


_config_module.get_data_dir = _fake_data_dir
_logger_module.get_data_dir = _fake_data_dir
# Start from a clean config (fresh defaults -> light theme first)
shutil.rmtree(_PREVIEW_CONFIG_DIR, ignore_errors=True)


def build_hypnogram(duration=600):
    """A synthetic but realistic sleep-stage sequence (per second)."""
    runs = [
        (60, 3),   # Wake at the start
        (110, 1),  # NREM
        (80, 2),   # REM
        (100, 1),  # NREM
        (50, 2),   # REM
        (40, 3),   # brief Wake
        (90, 1),   # NREM
        (50, 2),   # REM
        (20, 1),   # NREM tail
    ]
    states = []
    for sec, state in runs:
        states.extend([state] * sec)
    if len(states) < duration:
        states.extend([1] * (duration - len(states)))
    return states[:duration]


def _grab(window, path):
    pixmap = window.grab()
    pixmap.save(str(path))
    print(f"saved {path}")


def main():
    from PySide6.QtWidgets import QApplication

    from misleep.data import MiAnnotation
    from misleep.gui.config_dialog import SettingsDialog
    from misleep.gui.main_window import MainWindow

    app = QApplication.instance() or QApplication(sys.argv[:1])

    data_path = ROOT / "tests" / "data" / "10mins_example_mat.mat"
    out_dir = ROOT / "docs" / "imgs" / "gui"
    out_dir.mkdir(parents=True, exist_ok=True)

    window = MainWindow()
    window.resize(1360, 820)
    window.open_data(str(data_path))

    # Attach a synthetic annotation so the hypnogram and state colors show.
    window.mianno = MiAnnotation(
        build_hypnogram(window.total_seconds), state_map=window.state_map_dict)
    window.mianno.marker.append([185.5, "injection"])
    window.mianno.marker.append([340.0, "artifact"])
    window.mianno.start_end.append([130, 210, "spindle"])
    window.mianno.start_end.append([330, 380, "SWA"])
    window.show_duration = 120
    window.redraw_all(second=0)
    window.show()
    app.processEvents()

    _grab(window, out_dir / "main_light.png")

    dialog = SettingsDialog(window)
    dialog.show()
    app.processEvents()
    _grab(dialog, out_dir / "settings_light.png")
    dialog.close()

    window.toggle_theme()
    app.processEvents()
    _grab(window, out_dir / "main_dark.png")

    dialog = SettingsDialog(window)
    dialog.show()
    app.processEvents()
    _grab(dialog, out_dir / "settings_dark.png")
    dialog.close()

    window.is_saved = True
    window.close()
    print("previews written to", out_dir)


if __name__ == "__main__":
    main()
