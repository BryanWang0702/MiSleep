# -*- coding: UTF-8 -*-
"""Install / uninstall MiSleep file associations (double-click to open).

On **Windows** this registers the current user's (HKCU) file associations:

* ``.mat`` and ``.edf`` open in MiSleep by default,
* a right-click **"Open with MiSleep"** item is added for ``.txt``
  annotation files (without changing their default handler).

On **macOS / Linux** the script prints instructions instead (no
registry).

Usage (from the repository root)::

    python tools/install_file_associations.py            # install
    python tools/install_file_associations.py --uninstall

Notes
-----
* The previous default handler for ``.mat`` / ``.edf`` is backed up to
  ``~/.misleep/file_assoc_backup.json`` and restored by ``--uninstall``.
* Only affects the current user; no administrator rights are needed.
* The registered command uses ``pythonw.exe`` (when available) so that
  no console window flashes when you double-click a file.
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

#: Extensions that become the MiSleep default handler
DEFAULT_EXTENSIONS = [".mat", ".edf"]
#: Extensions that only get an "Open with MiSleep" context-menu item
CONTEXT_ONLY_EXTENSIONS = [".txt"]

PROGID = "MiSleep.Signal"
BACKUP_FILE = Path.home() / ".misleep" / "file_assoc_backup.json"


def _python_command() -> str:
    """Return the command template used to launch MiSleep with a file."""
    exe = Path(sys.executable)
    # Prefer pythonw on Windows to avoid a console window flashing
    if sys.platform == "win32":
        pythonw = exe.with_name("pythonw.exe")
        if pythonw.exists():
            return f'"{pythonw}" -m misleep "%1"'
    return f'"{exe}" -m misleep "%1"'


def _install_windows() -> None:
    import winreg

    command = _python_command()
    backup = {}

    # --- Default associations for .mat / .edf -------------------------
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{PROGID}") as key:
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "MiSleep recording file")
    with winreg.CreateKey(
            winreg.HKEY_CURRENT_USER, rf"Software\Classes\{PROGID}\DefaultIcon") as key:
        icon = Path(__file__).resolve().parents[1] / "src" / "misleep" / "gui" / "resources" / "logo.png"
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, str(icon))
    with winreg.CreateKey(
            winreg.HKEY_CURRENT_USER, rf"Software\Classes\{PROGID}\shell\open\command") as key:
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, command)

    for ext in DEFAULT_EXTENSIONS:
        reg_path = rf"Software\Classes\{ext}"
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                old, _ = winreg.QueryValueEx(key, "")
        except FileNotFoundError:
            old = None
        backup[ext] = old
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, PROGID)
        print(f"  registered default handler: {ext} -> MiSleep")

    # --- Context-menu item only for .txt ------------------------------
    for ext in CONTEXT_ONLY_EXTENSIONS:
        ctx_path = rf"Software\Classes\{ext}\shell\Open with MiSleep\command"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, ctx_path) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, command)
        print(f"  added context-menu item: {ext} -> 'Open with MiSleep'")

    _write_backup(backup)
    print(f"\nDone. Double-click a {', '.join(DEFAULT_EXTENSIONS)} file to open it "
          f"in MiSleep.\nCommand: {command}")


def _write_backup(backup: dict) -> None:
    BACKUP_FILE.parent.mkdir(parents=True, exist_ok=True)
    BACKUP_FILE.write_text(json.dumps(backup, indent=2), encoding="utf-8")


def _read_backup() -> dict:
    if BACKUP_FILE.exists():
        try:
            return json.loads(BACKUP_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _delete_tree(handle, sub_key) -> None:
    """Recursively delete a registry key and all its subkeys."""
    import winreg

    try:
        with winreg.OpenKey(handle, sub_key) as key:
            while True:
                try:
                    child = winreg.EnumKey(key, 0)
                except OSError:
                    break
                _delete_tree(key, child)
        winreg.DeleteKey(handle, sub_key)
    except FileNotFoundError:
        pass


def _uninstall_windows() -> None:
    import winreg

    backup = _read_backup()

    # --- context-menu item for .txt (delete only our subkey) ----------
    for ext in CONTEXT_ONLY_EXTENSIONS:
        ctx_cmd = rf"Software\Classes\{ext}\shell\Open with MiSleep\command"
        ctx_key = rf"Software\Classes\{ext}\shell\Open with MiSleep"
        ctx_shell = rf"Software\Classes\{ext}\shell"
        for path in (ctx_cmd, ctx_key, ctx_shell):
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, path)
            except FileNotFoundError:
                pass
        print(f"  removed context-menu item: {ext}")

    # --- default handlers for .mat / .edf -----------------------------
    for ext in DEFAULT_EXTENSIONS:
        reg_path = rf"Software\Classes\{ext}"
        old = backup.get(ext)
        if old:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, old)
            print(f"  restored previous handler for {ext}: {old}")
        else:
            # No previous handler: remove the default value we wrote, then
            # delete the key only when nothing else lives in it.
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0,
                                    winreg.KEY_SET_VALUE) as key:
                    winreg.DeleteValue(key, "")
                print(f"  removed association: {ext}")
            except FileNotFoundError:
                pass
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, reg_path)
            except (FileNotFoundError, PermissionError, OSError):
                pass  # key not empty (other software uses it) - leave it

    try:
        # Our ProgID key contains subkeys; remove the whole tree.
        _delete_tree(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{PROGID}")
        print(f"  removed ProgID: {PROGID}")
    except PermissionError as e:  # pragma: no cover
        print(f"  could not remove ProgID {PROGID}: {e}")

    try:
        BACKUP_FILE.unlink()
    except OSError:
        pass
    print("\nUninstalled. Double-click behavior restored.")


def _instructions_macos_linux() -> None:
    print("File associations are registered by the OS on this platform.")
    if sys.platform == "darwin":
        print("""
macOS (one time):
  1. Install `duti` (https://github.com/moretension/duti):
       brew install duti
  2. Create a bundle id for MiSleep, e.g. `org.misleep.app`, then run:
       duti -s org.misleep.app .mat all
       duti -s org.misleep.app .edf all
     (You must first make `misleep`/`python -m misleep` openable as an app
      via Automator or by wrapping it in an .app bundle.)
""")
    else:
        print("""
Linux (one time):
  cat > ~/.local/share/mime/packages/misleep.xml <<'EOF'
  <?xml version="1.0"?>
  <mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">
    <mime-type type="application/x-misleep-signal">
      <glob pattern="*.mat"/>
      <glob pattern="*.edf"/>
      <comment>MiSleep recording</comment>
    </mime-type>
  </mime-info>
  EOF
  update-mime-database ~/.local/share/mime
  xdg-mime default misleep.desktop application/x-misleep-signal
""")
    print("Tip: on every platform you can also open files from the command "
          "line:  misleep data.mat anno.txt")


def main():
    parser = argparse.ArgumentParser(
        description="Install/remove MiSleep file associations (double-click to open).")
    parser.add_argument("--uninstall", action="store_true",
                        help="Remove the associations and restore the previous handlers.")
    args = parser.parse_args()

    if sys.platform == "win32":
        if args.uninstall:
            _uninstall_windows()
        else:
            _install_windows()
    else:
        _instructions_macos_linux()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
