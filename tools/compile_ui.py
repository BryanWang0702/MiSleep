# -*- coding: UTF-8 -*-
"""Regenerate the PySide6 ``*_ui.py`` modules from the ``.ui`` files.

The generated modules live next to their ``.ui`` sources under
``src/misleep/gui/uis/``. They are committed to the repository so that
the package works without a Qt toolchain at install time; this script is
only needed when the ``.ui`` files change.

Usage (from the repository root)::

    python tools/compile_ui.py

Requires PySide6 (``pip install PySide6``).
"""

import shutil
import subprocess
import sys
from pathlib import Path

UI_DIR = Path(__file__).resolve().parents[1] / "src" / "misleep" / "gui" / "uis"


def _find_uic() -> str:
    """Locate the pyside6-uic executable."""
    exe = shutil.which("pyside6-uic") or shutil.which("pyside6-uic.exe")
    if exe:
        return exe
    # Fall back to the pip user Scripts directory
    for base in (Path.home() / "AppData" / "Roaming" / "Python", Path(sys.prefix) / "Scripts"):
        for scripts_dir in ([base] if base.name != "Python" else list(base.glob("Python*/Scripts"))):
            cand = scripts_dir / ("pyside6-uic.exe" if sys.platform == "win32" else "pyside6-uic")
            if cand.exists():
                return str(cand)
    raise RuntimeError("pyside6-uic not found. Install PySide6 (pip install PySide6).")


def main():
    ui_files = sorted(UI_DIR.glob("*.ui"))
    if not ui_files:
        print(f"No .ui files found in {UI_DIR}")
        return 1

    uic = _find_uic()
    for ui_file in ui_files:
        # <name>.ui -> <name>_ui.py (keeps the historical naming convention)
        out_file = ui_file.with_name(ui_file.stem + "_ui.py")
        cmd = [uic, str(ui_file), "-o", str(out_file)]
        print(f"  generating {out_file.name} ...")
        subprocess.run(cmd, check=True)
        _fix_resource_import(out_file)
    print(f"Regenerated {len(ui_files)} UI modules in {UI_DIR}")
    return 0


def _fix_resource_import(out_file: Path) -> None:
    """Point the generated 'import misleep_rc' at the package resource module."""
    text = out_file.read_text(encoding="utf-8")
    if "import misleep_rc" in text and "misleep.gui.resources" not in text:
        text = text.replace("import misleep_rc", "from misleep.gui.resources import misleep_rc")
        out_file.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
