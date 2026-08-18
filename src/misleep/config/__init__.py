# -*- coding: UTF-8 -*-
"""Configuration handling for MiSleep.

MiSleep is configured through an INI file with two sections:

* ``[gui]``  -- GUI behaviour (state map, state colors, markers, ...)
* ``[spec]`` -- spectral analysis defaults (window length, nfft, smoothing)

A default configuration is bundled with the package under
``misleep/config/default_config.ini``. On first run a *user* configuration
file is created at ``~/.misleep/misleep_config.ini`` and any user setting
overrides the bundled default, so package upgrades never wipe personal
settings.
"""

import configparser
import shutil
from pathlib import Path

from misleep.logger import get_data_dir, logger

#: Name of the per-user configuration file.
USER_CONFIG_NAME = "misleep_config.ini"


def default_config_path() -> Path:
    """Return the path of the bundled default configuration file."""
    import importlib.resources

    return Path(str(importlib.resources.files(__name__).joinpath("default_config.ini")))


def user_config_path() -> Path:
    """Return the path of the per-user configuration file."""
    return get_data_dir() / USER_CONFIG_NAME


def _ensure_user_config() -> Path:
    """Create the per-user configuration file on first use and return it."""
    path = user_config_path()
    if not path.exists():
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(default_config_path(), path)
            logger.info("Created user configuration at %s", path)
        except OSError:  # pragma: no cover
            logger.warning("Could not create user config at %s", path)
    return path


def load_config(path: str | Path | None = None) -> configparser.ConfigParser:
    """Load the effective MiSleep configuration.

    The bundled defaults are loaded first and then overridden by the
    per-user configuration file, so any key the user did not customize
    keeps its default value.

    Parameters
    ----------
    path : str | Path | None
        Explicit path to a configuration file. When ``None`` (default),
        the per-user configuration is used on top of the bundled default.

    Returns
    -------
    configparser.ConfigParser
        The merged configuration.
    """
    config = configparser.ConfigParser()
    config.read(default_config_path(), encoding="utf-8")

    if path is None:
        path = _ensure_user_config()
    if Path(path).exists():
        config.read(path, encoding="utf-8")
    else:
        logger.warning("Configuration file %s does not exist, using defaults", path)

    return config


def save_config(config: configparser.ConfigParser, path: str | Path | None = None) -> Path:
    """Persist a configuration back to disk.

    Parameters
    ----------
    config : configparser.ConfigParser
        The configuration to save.
    path : str | Path | None
        Destination file. Defaults to the per-user configuration file.

    Returns
    -------
    Path
        The file the configuration was written to.
    """
    if path is None:
        path = _ensure_user_config()
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        config.write(f)
    logger.info("Configuration saved to %s", path)
    return path
