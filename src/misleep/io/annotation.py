# -*- coding: UTF-8 -*-
"""Annotation file I/O.

The default MiSleep annotation format is a human readable ``.txt`` file
with three sections:

* ``==========Marker==========``     -- single time-point events
* ``==========Start-End==========``  -- start/end events
* ``==========Sleep state==========`` (or ``Sleep stage``) -- per-second states

A bio-signal annotation format (first two lines are a header, then
tab-separated state rows) is also supported through :func:`load_bio_anno`.
"""

import datetime
import json
import math
from pathlib import Path

from misleep.data import MiAnnotation
from misleep.io.base import MiData  # noqa: F401 (kept for API symmetry)
from misleep.logger import logger
from misleep.utils.annotation import (
    lst2group,
    marker2mianno,
    sleep_state2mianno,
    start_end2mianno,
)
from misleep.utils.time_utils import transfer_time


def load_misleep_anno(file_path, state_map=None):
    """Load annotations from a MiSleep annotation file.

    Parameters
    ----------
    file_path : str
        Path of the annotation file.
    state_map : dict, optional
        Custom state code -> name mapping.

    Returns
    -------
    MiAnnotation
        The parsed annotation.
    """
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        annotation = f.read().split("\n")

    if annotation == [""]:
        raise AssertionError("Empty")

    try:
        marker_idx = annotation.index("==========Marker==========")
        start_end_idx = annotation.index("==========Start-End==========")
        try:
            sleep_state_idx = annotation.index("==========Sleep state==========")
        except ValueError:
            sleep_state_idx = annotation.index("==========Sleep stage==========")
    except Exception:
        raise AssertionError("Invalid")

    marker = marker2mianno(annotation[marker_idx + 1: start_end_idx])
    start_end = start_end2mianno(annotation[start_end_idx + 1: sleep_state_idx])
    sleep_state = sleep_state2mianno(annotation[sleep_state_idx + 1:])

    return MiAnnotation(sleep_state=sleep_state, start_end=start_end,
                        marker=marker, state_map=state_map)


def load_bio_anno(file_path):
    """Load a bio-signal annotation file (tab-separated, 2-line header)."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        file = f.readlines()
    file = file[2:]
    state_list = [each.split("\t")[1] for each in file]
    state_list = [[each] * 4 for each in state_list]
    state_list = [item for each in state_list for item in each]
    state_map = {
        "AW": 3,
        "QW": 3,
        "NREM": 1,
        "REMS": 2,
    }
    state_list = [state_map[each] for each in state_list]

    return MiAnnotation(sleep_state=state_list, marker=[], start_end=[])


def load_json_anno(file_path, state_map=None):
    """Load a portable JSON annotation object.

    Required key: ``sleep_state``. Optional keys are ``marker``,
    ``start_end`` and ``state_map`` and mirror :class:`MiAnnotation`.
    """
    try:
        payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Invalid JSON annotation: {exc}") from exc
    if not isinstance(payload, dict) or "sleep_state" not in payload:
        raise ValueError("JSON annotation must be an object containing 'sleep_state'")
    mapping = payload.get("state_map", state_map)
    if mapping is not None:
        mapping = {int(key): str(value) for key, value in mapping.items()}
    return MiAnnotation(
        sleep_state=[int(value) for value in payload["sleep_state"]],
        marker=payload.get("marker", []),
        start_end=payload.get("start_end", []),
        state_map=mapping,
    )


def load_table_anno(file_path, state_map=None):
    """Load per-second or interval sleep states from CSV/TSV.

    Supported layouts (auto-detected; the header row is optional):

    * MiSleep-style tables: a ``state`` / ``state_code`` / ``sleep_state``
      column with optional ``start`` / ``end`` intervals (one row per
      second when no interval columns), plus optional ``type=marker`` /
      ``type=start_end`` event rows.
    * BIDS-style: ``onset`` / ``duration`` / ``stage`` (or ``label``) rows,
      e.g. ``sub-*_events.tsv``.
    * Epoch tables: ``[epoch index,] epoch second, epoch label`` - the
      index column may be missing (2 or 3 columns, with or without a
      header). Each row fills a 5 s epoch (or the detected epoch gap).
    """
    import numpy as np
    import pandas as pd

    path = Path(file_path)
    separator = "\t" if path.suffix.lower() == ".tsv" else ","
    raw = pd.read_csv(path, sep=separator, header=None, dtype=str)

    def _all_numeric(series):
        try:
            pd.to_numeric(series.dropna())
            return True
        except (TypeError, ValueError):
            return False

    # A header row is a row that is not fully numeric.
    if raw.shape[0] > 0 and not _all_numeric(raw.iloc[0]):
        columns = [str(column).strip().lower() for column in raw.iloc[0]]
        frame = raw.iloc[1:].reset_index(drop=True)
        frame.columns = columns[: frame.shape[1]]
        has_header = True
    else:
        frame = raw
        has_header = False

    mapping = state_map or {1: "NREM", 2: "REM", 3: "Wake", 4: "Init"}
    mapping = {int(key): str(value) for key, value in mapping.items()}
    reverse = {name.casefold(): code for code, name in mapping.items()}

    def state_code(value):
        try:
            code = int(float(value))
        except (TypeError, ValueError):
            code = reverse.get(str(value).strip().casefold())
        if code not in mapping:
            raise ValueError(f"Unknown sleep state {value!r}; expected {mapping}")
        return code

    def pick(*names):
        if not has_header:
            return None
        for name in names:
            if name in frame.columns:
                return name
        return None

    if has_header:
        state_col = pick("stage", "state", "state_code", "sleep_state", "label")
        start_col = pick("onset", "start")
        end_col = pick("end", "offset")
        duration_col = pick("duration")
        second_col = pick("epoch_second", "second", "time")
        index_col = pick("epoch", "epoch_index", "index")
        kind = frame["type"].astype(str).str.lower() if "type" in frame.columns else None
    else:
        state_col = frame.columns[frame.shape[1] - 1]
        second_col = frame.columns[frame.shape[1] - 2] if frame.shape[1] >= 2 else None
        index_col = frame.columns[frame.shape[1] - 3] if frame.shape[1] == 3 else None
        start_col = end_col = duration_col = None
        kind = None

    state_rows = frame if kind is None else frame[~kind.isin(["marker", "start_end", "event"])]
    if state_col is None or state_rows.empty:
        raise ValueError("Annotation table must contain sleep-state rows and a state column")

    if start_col is not None:
        starts = pd.to_numeric(state_rows[start_col], errors="coerce")
        if duration_col is not None:
            lengths = pd.to_numeric(state_rows[duration_col], errors="coerce")
            duration = int(math.ceil(float(starts.max() + lengths.max())))
        elif end_col is not None:
            ends = pd.to_numeric(state_rows[end_col], errors="coerce")
            lengths = ends - starts
            duration = int(math.ceil(float(ends.max())))
        else:
            lengths = None
            duration = int(math.ceil(float(starts.max()))) + 5
        sleep_state = [max(mapping)] * max(0, duration)
        for _, row in state_rows.iterrows():
            start = max(0, int(math.floor(float(row[start_col]))))
            ln = (int(math.ceil(float(row[duration_col])))
                  if duration_col is not None
                  else (int(math.ceil(float(row[end_col]) - float(row[start_col])))
                        if end_col is not None else 5))
            end = min(duration, start + max(1, ln))
            if end > start:
                sleep_state[start:end] = [state_code(row[state_col])] * (end - start)
    elif second_col is not None:
        # per-epoch rows: [index,] second, label -> fill 5 s epochs (or the
        # detected gap between consecutive seconds)
        starts = pd.to_numeric(state_rows[second_col], errors="coerce")
        ordered = np.sort(starts.dropna().values)
        gaps = np.diff(ordered)
        gaps = gaps[gaps > 0]
        epoch_len = int(gaps.min()) if gaps.size else 5
        duration = int(math.ceil(float(starts.max()))) + epoch_len
        sleep_state = [max(mapping)] * max(0, duration)
        for _, row in state_rows.iterrows():
            start = max(0, int(math.floor(float(row[second_col]))))
            end = min(duration, start + epoch_len)
            if end > start:
                sleep_state[start:end] = [state_code(row[state_col])] * (end - start)
    else:
        # one row per second
        sleep_state = [state_code(value) for value in state_rows[state_col]]

    marker, start_end = [], []
    if kind is not None:
        for index, row in frame[kind == "marker"].iterrows():
            when = row.get("time", row.get("start"))
            marker.append([float(when), str(row.get("label", "marker"))])
        for index, row in frame[kind.isin(["start_end", "event"])].iterrows():
            start_end.append([float(row["start"]), float(row["end"]),
                              str(row.get("label", "event"))])
    return MiAnnotation(sleep_state=sleep_state, marker=marker,
                        start_end=start_end, state_map=mapping)


def available_annotation_readers():
    """Return annotation extensions understood by :func:`load_annotation`."""
    return [".txt", ".json", ".csv", ".tsv"]


def load_annotation(file_path, state_map=None):
    """Load an annotation by extension, auto-detecting legacy TXT files."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Annotation file not found: {path}")
    suffix = path.suffix.lower()
    if suffix == ".json":
        return load_json_anno(path, state_map=state_map)
    if suffix in (".csv", ".tsv"):
        return load_table_anno(path, state_map=state_map)
    if suffix == ".txt":
        prefix = path.read_text(encoding="utf-8", errors="ignore")[:5]
        return load_bio_anno(path) if prefix == "Start" else load_misleep_anno(path, state_map)
    raise ValueError(f"Unsupported annotation extension {suffix!r}")


def save_misleep_anno(mianno, midata, file_path):
    """Write a :class:`MiAnnotation` to the MiSleep ``.txt`` format.

    Parameters
    ----------
    mianno : MiAnnotation
        The annotation to save.
    midata : MiData
        The associated data (used for the acquisition time).
    file_path : str
        Destination file.

    Returns
    -------
    bool
        True on success.
    """
    from misleep.utils.time_utils import second2time

    ac_time = datetime.datetime.strptime(midata.time, "%Y%m%d-%H:%M:%S")

    marker = [", ".join([
        second2time(round(each[0], 3), ac_time=ac_time, ms=True), str(round(each[0], 3)), "1",
        second2time(round(each[0], 3), ac_time=ac_time, ms=True), str(round(each[0], 3)), "0",
        "1", each[1]
    ]) for each in mianno.marker]

    start_end_label = [", ".join([
        second2time(round(each[0], 3), ac_time=ac_time, ms=True), str(round(each[0], 3)), "1",
        second2time(round(each[1], 3), ac_time=ac_time, ms=True), str(round(each[1], 3)), "0",
        "1", each[2]
    ]) for each in mianno.start_end]

    sleep_state = lst2group([[idx, each] for idx, each in enumerate(mianno.sleep_state)])
    sleep_state = [", ".join([
        second2time(each[0], ac_time=ac_time), str(each[0]), "1",
        second2time(each[1], ac_time=ac_time), str(each[1]),
        "0", str(each[2]), mianno.state_map[each[2]]
    ]) for each in sleep_state]

    if len(marker) > 0:
        marker = [""] + marker
    if len(start_end_label) > 0:
        start_end_label = [""] + start_end_label

    annos = [
        "READ ONLY! DO NOT EDIT!\n4-INIT 3-Wake 2-REM 1-NREM",
        "Save time: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Acquisition time: " + ac_time.strftime("%Y-%m-%d %H:%M:%S"),
        "==========Marker==========" + "\n".join(marker),
        "==========Start-End==========" + "\n".join(start_end_label),
        "==========Sleep stage==========", "\n".join(sleep_state)
    ]

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(annos))
    return True


def transfer_result(mianno, ac_time):
    """Convert a :class:`MiAnnotation` into analysis dataframes.

    Produces per-hour sleep statistics (duration, bout count, average bout
    length, percentage for every state), plus a 12h light/dark phase
    summary. Also returns the raw marker/start-end dataframes.

    Parameters
    ----------
    mianno : MiAnnotation
        Annotation to transfer.
    ac_time : datetime.datetime
        Acquisition time of the recording.

    Returns
    -------
    (df, analyse_df, start_end_df, marker_df) : tuple of pandas.DataFrame
    """
    import pandas as pd

    marker = [[
        transfer_time(ac_time, each[0], "%Y-%m-%d %H:%M:%S", ms=True),
        each[0], each[1]] for each in mianno.marker]

    start_end_label = [[
        transfer_time(ac_time, each[0], "%Y-%m-%d %H:%M:%S", ms=True), each[0], 1,
        transfer_time(ac_time, each[1], "%Y-%m-%d %H:%M:%S", ms=True), each[1], 0,
        each[2], each[1] - each[0]
    ] for each in mianno.start_end]

    # Split the sleep state into per-hour groups
    sleep_state = []
    for each in range(int(len(mianno.sleep_state) / 3600) + 1):
        temp_hour_label = mianno.sleep_state[each * 3600: (each + 1) * 3600]
        if temp_hour_label != []:
            sleep_state.append(temp_hour_label)

    marker_sleep_state = []
    for hour, label in enumerate(sleep_state):
        hour_sleep_state = lst2group(
            [idx + hour * 3600, each] for idx, each in enumerate(label))
        marker_sleep_state += [[
            transfer_time(ac_time, each[0], "%Y-%m-%d %H:%M:%S"), each[0], 1,
            transfer_time(ac_time, each[1], "%Y-%m-%d %H:%M:%S"), each[1], 0,
            each[2], mianno.state_map[each[2]], each[1] - each[0], hour
        ] for each in hour_sleep_state]

        marker_sleep_state += [[
            transfer_time(ac_time, (hour + 1) * 3600, "%Y-%m-%d %H:%M:%S"), (hour + 1) * 3600, 1,
            transfer_time(ac_time, (hour + 1) * 3600, "%Y-%m-%d %H:%M:%S"), (hour + 1) * 3600, 0,
            5, "MARKER", "", ""]]

    columns = ["start_time", "start_time_sec", "start_code",
               "end_time", "end_time_sec", "end_code",
               "state_code", "state", "bout_duration", "hour"]

    df = pd.DataFrame(data=marker_sleep_state, columns=columns)

    df["hour"] = df.apply(
        lambda x: "" if x["state"] == "MARKER" else int(x["start_time_sec"] / 3600), axis=1)
    analyse_df = pd.DataFrame()

    temp_hour = list(set(list(df["hour"])))
    temp_hour.remove("")
    temp_hour = sorted(temp_hour)
    analyse_df["date_time"] = [transfer_time(ac_time, each * 3600, "%Y-%m-%d %H:%M:%S")
                               for each in temp_hour]

    features = []
    for each in temp_hour:
        df_ = df[df["hour"] == each]
        temp_lst = []
        for phase in ["NREM", "REM", "Wake", "INIT"]:
            _duration = df_[df_["state"] == phase]["bout_duration"].sum()
            _bout = df_[df_["state"] == phase]["bout_duration"].count()
            temp_lst += [_duration, _bout, round(_duration / _bout, 2) if _bout != 0 else 0,
                         round(_duration / 3600, 4) * 100]
        features.append(temp_lst)

    analyse_df[["NREM_duration", "NREM_bout", "NREM_ave", "NREM_percentage",
                "REM_duration", "REM_bout", "REM_ave", "REM_percentage",
                "WAKE_duration", "WAKE_bout", "WAKE_ave", "WAKE_percentage",
                "INIT_duration", "INIT_bout", "INIT_ave", "INIT_percentage"]] = features

    analyse_df[["NREM_duration", "NREM_bout", "REM_duration", "REM_bout", "WAKE_duration",
                "WAKE_bout", "INIT_duration", "INIT_bout"]] = analyse_df[
        ["NREM_duration", "NREM_bout", "REM_duration", "REM_bout", "WAKE_duration",
         "WAKE_bout", "INIT_duration", "INIT_bout"]].astype(int)

    # 12-h light/dark phase summary (first hour treated as ZT0 by default)
    try:
        phase_data = pd.DataFrame()
        phase_data["date_time"] = ["ZT0-ZT12", "ZT12-ZT24"]
        for phase in ["NREM", "REM", "WAKE", "INIT"]:
            duration_key = f"{phase}_duration"
            bout_key = f"{phase}_bout"
            ave_key = f"{phase}_ave"
            pct_key = f"{phase}_percentage"
            phase_data[duration_key] = [analyse_df[duration_key].iloc[:12].sum(),
                                        analyse_df[duration_key].iloc[12:24].sum()]
            phase_data[bout_key] = [analyse_df[bout_key].iloc[:12].sum(),
                                    analyse_df[bout_key].iloc[12:24].sum()]
            phase_data[ave_key] = phase_data.apply(
                lambda x: x[duration_key] / x[bout_key] if x[bout_key] != 0 else 0, axis=1)
            phase_data[pct_key] = phase_data.apply(lambda x: x[duration_key] / (3600 * 12), axis=1)

        analyse_df = pd.concat([analyse_df, phase_data])
        analyse_df.reset_index(inplace=True)
    except Exception as e:
        logger.warning(f"Could not compute light/dark phase summary: {e}")

    start_end_df = pd.DataFrame(
        start_end_label,
        columns=["start_time", "start_time_sec", "start_code",
                 "end_time", "end_time_sec", "end_code",
                 "label", "bout_duration"])

    marker_df = pd.DataFrame(marker, columns=["timestamp", "timestamp_sec", "label"])

    return df, analyse_df, start_end_df, marker_df
