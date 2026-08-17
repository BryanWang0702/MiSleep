# -*- coding: UTF-8 -*-
"""EDF (European Data Format) file reader/writer.

Uses the ``pyedflib`` package for both reading and writing.
"""

import datetime

from misleep.data import MiData
from misleep.io.base import register_signal_reader, register_signal_writer
from misleep.logger import logger

_TIME_FORMAT = "%Y%m%d-%H:%M:%S"


def load_edf(data_path):
    """Load an EDF/EDF+ file into a :class:`MiData`.

    Parameters
    ----------
    data_path : str
        Path of the ``.edf`` file.

    Returns
    -------
    MiData
        The loaded data.
    """
    import pyedflib

    signals, signal_headers, meta = pyedflib.highlevel.read_edf(edf_file=data_path)

    return MiData(
        signals=signals,
        channels=[each["label"] for each in signal_headers],
        sf=[each["sample_frequency"] for each in signal_headers],
        time=meta["startdate"].strftime(_TIME_FORMAT),
    )


def write_edf(signals, channels, sf, time, edf_file=None):
    """Write signal data to an EDF file.

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
    edf_file : str, optional
        Destination path. Defaults to a timestamped file in the current
        directory.

    Returns
    -------
    None
    """
    import pyedflib

    if edf_file is None:
        edf_file = f"./{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_saved.edf"

    header = {
        "technician": "",
        "recording_additional": "",
        "patientname": "MiSleep",
        "patient_additional": "",
        "patientcode": "",
        "equipment": "",
        "admincode": "",
        "sex": "",
        "startdate": datetime.datetime.strptime(time, _TIME_FORMAT),
        "birthdate": "",
    }

    signal_headers = [
        {
            "label": each,
            "dimension": "uV",
            "sample_frequency": sf[idx],
            "physical_max": 10417.0,
            "physical_min": -10417.0,
            "digital_max": 32767,
            "digital_min": -32768,
            "prefilter": "",
            "transducer": "",
        }
        for idx, each in enumerate(channels)
    ]

    try:
        with pyedflib.EdfWriter(edf_file, len(signals)) as edf_writer:
            edf_writer.setHeader(header)
            for i, signal in enumerate(signals):
                edf_writer.setSignalHeader(i, signal_headers[i])
            edf_writer.writeSamples(signals)
        logger.info("Data written to %s", edf_file)
    except Exception as e:
        logger.error(f"Write data ERROR: {e}")


register_signal_reader(".edf", load_edf)
register_signal_writer(".edf", write_edf)
