# -*- coding: UTF-8 -*-
"""Input/output module: loading and saving signals and annotations.

The module is organised around two light-weight registries (readers and
writers) that map file extensions to callables. Third-party code can
register new formats either programmatically

.. code-block:: python

    from misleep.io.base import register_signal_reader
    register_signal_reader(".xyz", my_xyz_reader)

or declaratively through the ``misleep.signal_readers`` / ``misleep.signal_writers``
entry-point groups (see the project's ``pyproject.toml``).
"""

import importlib.metadata
from pathlib import Path

from misleep.data import MiData, MiAnnotation  # backward-compatible re-export

__all__ = [
    "MiData",
    "MiAnnotation",
    "register_signal_reader",
    "register_signal_writer",
    "load_signal",
    "write_signal",
    "available_readers",
    "available_writers",
]

#: Built-in readers/writers: extension (lower-case, with dot) -> callable.
_BUILTIN_READERS: dict[str, callable] = {}
_BUILTIN_WRITERS: dict[str, callable] = {}
_ENTRYPOINT_READERS: dict[str, callable] | None = None
_ENTRYPOINT_WRITERS: dict[str, callable] | None = None


def register_signal_reader(extension: str, func: callable) -> None:
    """Register a callable that loads a :class:`MiData` from ``extension`` files.

    Parameters
    ----------
    extension : str
        File extension including the dot, e.g. ``".mat"``. Matching is
        case-insensitive.
    func : callable
        ``func(path: str) -> MiData``.
    """
    _BUILTIN_READERS[extension.lower()] = func


def register_signal_writer(extension: str, func: callable) -> None:
    """Register a callable that saves a :class:`MiData` to ``extension`` files.

    Parameters
    ----------
    extension : str
        File extension including the dot, e.g. ``".edf"``.
    func : callable
        ``func(signals, channels, sf, time, file_path) -> None``.
    """
    _BUILTIN_WRITERS[extension.lower()] = func


def _load_entry_points(group: str) -> dict[str, callable]:
    """Load third-party entry points for a given group (best effort)."""
    registry: dict[str, callable] = {}
    try:
        eps = importlib.metadata.entry_points()
        if hasattr(eps, "select"):
            matches = eps.select(group=group)
        else:  # pragma: no cover - Python < 3.10
            matches = eps.get(group, [])
        for ep in matches:
            try:
                func = ep.load()
                registry[ep.name.lower()] = func
            except Exception:
                continue
    except Exception:
        pass
    return registry


def _all_readers() -> dict[str, callable]:
    global _ENTRYPOINT_READERS
    if _ENTRYPOINT_READERS is None:
        _ENTRYPOINT_READERS = _load_entry_points("misleep.signal_readers")
    return {**_ENTRYPOINT_READERS, **_BUILTIN_READERS}


def _all_writers() -> dict[str, callable]:
    global _ENTRYPOINT_WRITERS
    if _ENTRYPOINT_WRITERS is None:
        _ENTRYPOINT_WRITERS = _load_entry_points("misleep.signal_writers")
    return {**_ENTRYPOINT_WRITERS, **_BUILTIN_WRITERS}


def available_readers() -> list[str]:
    """List the registered file extensions that can be loaded."""
    return sorted(_all_readers().keys())


def available_writers() -> list[str]:
    """List the registered file extensions that can be saved."""
    return sorted(_all_writers().keys())


def load_signal(data_path: str | Path):
    """Load a signal file by dispatching on its extension.

    Parameters
    ----------
    data_path : str or Path
        Path of the file to load (``.mat``, ``.edf`` or any registered
        extension).

    Returns
    -------
    MiData
        The loaded data.
    """
    suffix = Path(data_path).suffix.lower()
    readers = _all_readers()
    if suffix not in readers:
        raise ValueError(
            f"Unsupported file extension '{suffix}'. "
            f"Registered readers: {sorted(readers)}"
        )
    return readers[suffix](str(data_path))


def write_signal(midata, file_path: str | Path) -> None:
    """Save a :class:`MiData` by dispatching on the target extension.

    Parameters
    ----------
    midata : MiData
        Data to save.
    file_path : str or Path
        Destination file (``.mat``, ``.edf`` or any registered extension).
    """
    suffix = Path(file_path).suffix.lower()
    writers = _all_writers()
    if suffix not in writers:
        raise ValueError(
            f"Unsupported file extension '{suffix}'. "
            f"Registered writers: {sorted(writers)}"
        )
    writers[suffix](midata.signals, midata.channels, midata.sf, midata.time, str(file_path))
