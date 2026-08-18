# -*- coding: UTF-8 -*-
"""Helpers for converting between annotation representations."""

from misleep.utils.time_utils import transfer_time


def lst2group(pre_lst):
    """Group consecutive rows of a two-column list into ``[start, end, value]`` triples.

    Converts a list like ``[[1, 2], [2, 2], [3, 2], [4, 2], [5, 2], [6, 1], [7, 1], ...]``
    into ``[[1, 6, 2], [6, 9, 1], ...]`` where the second element of each
    triple is an *exclusive* end index.

    Parameters
    ----------
    pre_lst : list of [index, value]
        Sorted list of ``[index, value]`` pairs.

    Returns
    -------
    list of [start, end, value]
        Consecutive runs, ``end`` is exclusive.
    """
    rows = iter(pre_lst)
    try:
        first_idx, first_value = next(rows)
    except StopIteration:
        return []

    grouped = []
    run_start = last_idx = first_idx
    run_value = first_value
    for idx, value in rows:
        if value != run_value:
            grouped.append([run_start, last_idx + 1, run_value])
            run_start = idx
            run_value = value
        last_idx = idx
    grouped.append([run_start, last_idx + 1, run_value])
    return grouped


def marker2mianno(marker):
    """Convert MiSleep annotation lines to ``[[time, label], ...]`` markers."""
    if marker != [] or marker is not None:
        marker = [each.split(", ") for each in marker]
        marker = [[float(each[1]), each[7]] for each in marker]
        return marker
    return []


def start_end2mianno(start_end):
    """Convert MiSleep annotation lines to ``[[start, end, label], ...]`` events."""
    if start_end != [] or start_end is not None:
        start_end = [each.split(", ") for each in start_end]
        start_end = [[float(each[1]), float(each[4]), each[7]] for each in start_end]
        return start_end
    return []


def sleep_state2mianno(sleep_state):
    """Convert MiSleep annotation lines to a per-second state sequence."""
    start_end = [each.split(", ") for each in sleep_state]
    # Old version misleep labels start from 1
    if start_end[0][1] == "1":
        sleep_state = [item for each in start_end for item in [int(each[6])] * (int(each[4]) - int(each[1]) + 1)]
    else:
        sleep_state = [item for each in start_end for item in [int(each[6])] * (int(each[4]) - int(each[1]))]
    return sleep_state


def insert_row(df, idx, row):
    """Insert a row into a dataframe at a specific position.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataframe to insert into.
    idx : int
        Position to insert the row (inserted below this index).
    row : pandas.Series or DataFrame
        Row to insert.

    Returns
    -------
    pandas.DataFrame
        A new dataframe with the row inserted.
    """
    import pandas as pd

    if isinstance(row, pd.Series):
        row = pd.DataFrame(row).T
    df = pd.concat([df[:idx], row, df[idx:]], axis=0).reset_index(drop=True)
    return df


def temp_loop4below_row(row, acquisition_time, columns):
    """Split a row that crosses an hour boundary into three rows.

    Used when exporting per-hour sleep statistics: a long bout that
    straddles a full hour is split into "before hour", an hourly
    ``MARKER`` divider row, and "after hour".

    Returns
    -------
    (previous_row, new_row, below_row) : tuple of pandas.Series
    """
    import pandas as pd

    seconds_ = (int(row["start_time_sec"] / 3600) + 1) * 3600
    previous_row = pd.Series([
        row["start_time"], row["start_time_sec"], "1",
        transfer_time(acquisition_time, seconds_, "%Y-%m-%d %H:%M:%S"),
        seconds_, "0", row["state_code"], row["state"]
    ], index=columns)

    new_row = pd.Series([
        transfer_time(acquisition_time, seconds_, "%Y-%m-%d %H:%M:%S"),
        seconds_, " ",
        transfer_time(acquisition_time, seconds_, "%Y-%m-%d %H:%M:%S"),
        seconds_, " ", "5", "MARKER"
    ], index=columns)

    below_row = pd.Series([
        transfer_time(acquisition_time, seconds_ + 1, "%Y-%m-%d %H:%M:%S"),
        seconds_ + 1, "1", row["end_time"], row["end_time_sec"],
        "0", row["state_code"], row["state"]
    ], index=columns)

    return previous_row, new_row, below_row
