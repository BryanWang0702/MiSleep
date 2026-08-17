# -*- coding: UTF-8 -*-
"""Time helpers: add seconds to an acquisition time and format it."""

import datetime


def transfer_time(date_time, seconds, date_time_format="%d:%H:%M:%S", ms=False):
    """Add ``seconds`` to a datetime and format it.

    Parameters
    ----------
    date_time : datetime.datetime
        The starting datetime (typically the recording acquisition time).
    seconds : int or float
        Seconds to add.
    date_time_format : str
        Output strftime format. Defaults to ``'%d:%H:%M:%S'``.
    ms : bool
        Whether to keep the millisecond part in the output.

    Returns
    -------
    str
        The formatted target time.

    Examples
    --------
    >>> import datetime
    >>> transfer_time(datetime.datetime(2024, 1, 30, 10, 50, 0), 40)
    '30-10:50:40'
    """
    temp_time = date_time + datetime.timedelta(seconds=seconds)
    if ms:
        seconds_str = str(seconds)
        ms_part = seconds_str.split(".")[1] if "." in seconds_str else "000"
        return f"{temp_time.strftime(date_time_format)}.{ms_part}"
    return temp_time.strftime(date_time_format)


def second2time(second, ac_time, ms=False):
    """Format a number of seconds relative to the acquisition time.

    Parameters
    ----------
    second : int or float
        Seconds since acquisition.
    ac_time : datetime.datetime
        Acquisition time.
    ms : bool
        Whether to keep the millisecond part.

    Returns
    -------
    str
        Time formatted as ``DD:HH:MM:SS`` (with ``.mmm`` when ``ms=True``).
    """
    if ms:
        seconds_str = str(second)
        ms_part = seconds_str.split(".")[1] if "." in seconds_str else "000"
        return (ac_time + datetime.timedelta(seconds=second)).strftime(f"%d:%H:%M:%S:{ms_part}")
    return (ac_time + datetime.timedelta(seconds=second)).strftime("%d:%H:%M:%S")
