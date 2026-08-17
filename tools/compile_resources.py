# -*- coding: UTF-8 -*-
"""Compile the Qt resource file (``misleep.qrc``) into a Python module.

The generated ``misleep_rc.py`` lives in ``src/misleep/gui/resources/`` and
is committed to the repository. Run this script only when the resource
files (logo images) change.

Usage (from the repository root)::

    python tools/compile_resources.py

Requires PySide6 (``pip install PySide6``).
"""

import shutil
import subprocess
import sys
from pathlib import Path

RES_DIR = Path(__file__).resolve().parents[1] / "src" / "misleep" / "gui" / "resources"


def _find_rcc() -> str:
    """Locate the pyside6-rcc executable."""
    exe = shutil.which("pyside6-rcc") or shutil.which("pyside6-rcc.exe")
    if exe:
        return exe
    for base in (Path.home() / "AppData" / "Roaming" / "Python", Path(sys.prefix) / "Scripts"):
        for scripts_dir in ([base] if base.name != "Python" else list(base.glob("Python*/Scripts"))):
            cand = scripts_dir / ("pyside6-rcc.exe" if sys.platform == "win32" else "pyside6-rcc")
            if cand.exists():
                return str(cand)
    raise RuntimeError("pyside6-rcc not found. Install PySide6 (pip install PySide6).")


def main():
    qrc_file = RES_DIR / "misleep.qrc"
    if not qrc_file.exists():
        print(f"No misleep.qrc found in {RES_DIR}")
        return 1

    out_file = RES_DIR / "misleep_rc.py"
    cmd = [_find_rcc(), str(qrc_file), "-o", str(out_file)]
    print(f"  compiling {qrc_file.name} -> {out_file.name} ...")
    subprocess.run(cmd, check=True)
    print(f"Compiled {out_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
