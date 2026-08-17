# -*- coding: UTF-8 -*-
"""MATLAB ``.mat`` file reader/writer.

Supports all three common MAT variants:

* v5 / v7  -- loaded with :func:`scipy.io.loadmat`
* v7.3     -- loaded with the pure-python ``mat73`` package
* python-saved MiSleep files (identified by a ``save = 'python'`` entry)

Writing always produces a v5 ``.mat`` file compatible with MATLAB R14+.
"""

import datetime
import re

import numpy as np
from scipy.io import loadmat as scipy_loadmat
from scipy.io import savemat

from misleep.data import MiData
from misleep.logger import logger
from misleep.io.base import register_signal_reader, register_signal_writer

#: Regex for the MiSleep acquisition-time format ``YYYYMMDD-HH:MM:SS``
_TIME_FORMAT = "%Y%m%d-%H:%M:%S"


def _load_scipy(raw_data):
    """Parse a dict produced by scipy.io.loadmat into a MiData."""
    names = raw_data.dtype.names

    # Old version misleep data: raw 2-D numeric array without structure
    if names is None:
        if raw_data.shape[0] > raw_data.shape[1]:
            signals = raw_data.T
        else:
            signals = raw_data
        channels = [f"ch{each + 1}" for each in range(signals.shape[0])]
        sf = [305.0 for _ in range(signals.shape[0])]
        time = datetime.datetime.now().strftime(_TIME_FORMAT)
        return MiData(signals=signals, channels=channels, sf=sf, time=time)

    raw_data = raw_data[0][0]

    # Saved by python: channels listed first, then metadata fields
    if "save" in names:
        channels = list(names[:-4])
        sf = [float(each) for each in raw_data["sf"][0]]
        signals = [raw_data[each][0] for each in channels]
        time = raw_data["time"][0]
        return MiData(signals=signals, channels=channels, sf=sf, time=time)

    # Saved by matlab
    channels = [each for item in raw_data["channels"][0] for each in item]
    sf = [float(each[0]) for item in raw_data["sf"][0] for each in item]
    signals = []
    for each in channels:
        signal_ = raw_data[each]
        if signal_.shape[0] > signal_.shape[1]:
            signals.append(signal_.T[0])
        if signal_.shape[0] < signal_.shape[1]:
            signals.append(signal_[0])

    try:
        time = raw_data["time"][0][0][0]
        datetime.datetime.strptime(time, _TIME_FORMAT)
    except (ValueError, TypeError):
        time = raw_data["time"][0]

    return MiData(signals=signals, channels=channels, sf=sf, time=time)


def _load_mat73(raw_data):
    """Parse a dict produced by mat73.loadmat into a MiData."""
    try:
        _ = raw_data["channels"]
    except (KeyError, TypeError):
        # Old version misleep data: raw numeric array
        if raw_data.shape[0] > raw_data.shape[1]:
            signals = raw_data.T
        else:
            signals = raw_data
        channels = [f"ch{each + 1}" for each in range(signals.shape[0])]
        sf = [305.0 for _ in range(signals.shape[0])]
        time = datetime.datetime.now().strftime(_TIME_FORMAT)
        return MiData(signals=signals, channels=channels, sf=sf, time=time)

    channels = list(raw_data["channels"])
    sf = [float(each) for each in raw_data["sf"]]
    time = raw_data["time"][0]

    signals = []
    for each in channels:
        signal_ = raw_data[each]
        if signal_.shape[0] > 1:
            signals.append(signal_)
        if signal_.shape[0] == 1:
            signals.append(signal_.T)

    return MiData(signals=signals, channels=channels, sf=sf, time=time)


def load_mat(data_path):
    """Load a ``.mat`` file into a :class:`MiData`.

    The loader automatically detects the MAT version (v5, v7 or v7.3) and
    the origin of the file (MATLAB vs. MiSleep/python saved).

    Parameters
    ----------
    data_path : str
        Path of the ``.mat`` file.

    Returns
    -------
    MiData or None
        The loaded data, or ``None`` when the file could not be parsed.
    """
    try:
        raw_data = list(scipy_loadmat(data_path).values())[-1]
        return _load_scipy(raw_data)
    except NotImplementedError:
        # v7.3 file -> use mat73
        try:
            from mat73 import loadmat as mat73_loadmat

            raw_data = list(mat73_loadmat(data_path).values())[-1]
            return _load_mat73(raw_data)
        except Exception as e:
            logger.error(f"Load data ERROR: {e}")
            return None
    except Exception as e:
        logger.error(f"Load data ERROR: {e}")
        return None


def write_mat(signals, channels, sf, time, mat_file=None):
    """Write signal data to a v5 ``.mat`` file.

    Parameters
    ----------
    signals : list of ndarray
        Signal data, one array per channel.
    channels : list of str
        Channel names.
    sf : list of float
        Sampling frequencies.
    time : str
        Acquisition time in ``YYYYMMDD-HH:MM:SS`` format.
    mat_file : str, optional
        Destination path. Defaults to a timestamped file in the current
        directory.

    Returns
    -------
    None
    """
    if mat_file is None:
        mat_file = f"./{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_saved.mat"

    mdict = {"data": dict(zip(channels, signals))}
    mdict["data"]["save"] = "python"
    mdict["data"]["channels"] = channels
    mdict["data"]["sf"] = sf
    mdict["data"]["time"] = time

    savemat(file_name=mat_file, mdict=mdict, format="5", oned_as="row")
    logger.info("Data written to %s", mat_file)


register_signal_reader(".mat", load_mat)
register_signal_writer(".mat", write_mat)


def _legacy_time_to_seconds(time_str: str) -> int:
    """Convert a MiSleep time string to seconds since the day start."""
    parts = [int(x) for x in time_str.split("-")[-1].split(":")]
    return ((parts[0] * 60) + parts[1]) * 60 + parts[2]


def get_start_second(acquisition_time_str: str) -> int:
    """Return the second-of-day of an acquisition time (helper for exports)."""
    m = re.match(r"(\d{4})(\d{2})(\d{2})-(\d{2}):(\d{2}):(\d{2})", acquisition_time_str)
    if not m:
        raise ValueError(f"Invalid acquisition time: {acquisition_time_str!r}")
    _, _, _, hh, mm, ss = (int(g) for g in m.groups())
    return hh * 3600 + mm * 60 + ss
