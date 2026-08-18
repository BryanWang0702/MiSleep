# -*- coding: UTF-8 -*-
"""Compatibility helpers so MiSleep runs on Python 3.8 through 3.14.

Only packaging/resource helpers live here; there is no application logic.
"""

from pathlib import Path


def resource_dir(package: str) -> Path:
    """Return the filesystem directory of a package (3.8-compatible)."""
    try:
        from importlib.resources import files

        return Path(str(files(package)))
    except (ImportError, AttributeError):  # pragma: no cover - Python 3.8
        import importlib

        return Path(str(importlib.import_module(package).__path__[0]))


def resource_path(package: str, name: str) -> Path:
    """Return the filesystem path of a package resource file.

    ``importlib.resources.files`` (Python 3.9+) is preferred; on Python
    3.8 the older ``importlib.resources.path`` is used instead.
    """
    try:
        from importlib.resources import files

        return Path(str(files(package).joinpath(name)))
    except (ImportError, AttributeError):  # pragma: no cover - Python 3.8
        import importlib.resources

        with importlib.resources.path(package, name) as path:
            return Path(str(path))
