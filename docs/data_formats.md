# Data formats

MiSleep works with two kinds of files: **signal files** (raw recordings)
and **annotation files** (scoring).

## Signal files

The GUI and `misleep.load_signal(path)` use the same extension registry.
Built-in readers currently cover `.mat`, `.edf`, `.bdf`, `.npy`, `.npz`,
`.csv` and `.tsv`. Extension matching is case-insensitive.

### NumPy `.npz` (recommended Python interchange)

NPZ is self-contained, compressed and supports channels with different sample
counts. MiSleep archives store `signal_0`, `signal_1`, … plus `channels`, `sf`
and `time`; they never require pickle support.

```python
from misleep import load_signal, write_npz

write_npz(data.signals, data.channels, data.sf, data.time, "recording.npz")
loaded = load_signal("recording.npz")
```

### NumPy `.npy`

NPY stores a numeric 1-D or 2-D array. Since an array has no standard sampling
frequency field, put metadata in `recording.npy.json` (or `recording.json`):

```json
{
  "sf": [256, 256],
  "channels": ["EEG", "EMG"],
  "time": "20240409-18:00:00",
  "channel_axis": 0,
  "describe": "optional note"
}
```

`sf` is required and can be one number (applied to every channel) or one per
channel. `channel_axis` is `0` for channels × samples and `1` for samples ×
channels; if omitted, MiSleep treats the smaller dimension as channels. For
security, object arrays that need `allow_pickle=True` are rejected.

### CSV / TSV

The first row contains channel names and every later row contains samples. A
column named `time`, `times`, `second`, `seconds` or `timestamp` is used to
infer the sampling frequency from its median step:

```csv
time,EEG,EMG
0.000,12.1,4.2
0.004,11.8,4.0
```

Without a time column, add the same JSON sidecar described for NPY. Large or
mixed-frequency recordings are better stored as NPZ, EDF/BDF or MAT.

### MATLAB `.mat`

Three variants are supported and auto-detected:

1. **MATLAB v5 / v7** — loaded with `scipy.io.loadmat`.
2. **MATLAB v7.3** (HDF5-based, > 2 GB files) — loaded with the pure
   Python `mat73` package.
3. **Python/MiSleep saved** — identified by a `save = 'python'` entry.

The recommended layout (used by the GUI's "Save Data" function) is a
MATLAB struct with one field per channel plus three metadata fields:

```matlab
data.EEG      = [1 x N] double;
data.EMG_DIFF = [1 x N] double;
data.channels = {'EEG', 'EMG_DIFF'};   % cell array of channel names
data.sf       = [256, 256];            % sampling frequency per channel
data.time     = '20240409-18:00:00';   % acquisition time (string)
```

Any additional fields are ignored. When loading, all channels are
truncated to the same integer duration in seconds.

### EDF / EDF+

The [European Data Format](https://edfplus.info/) is a standard, widely
supported format. Loading is done with `pyedflib`; the acquisition time
and per-channel sampling frequencies are read from the file header.
Saving uses 16-bit digital scaling with a ±10417 µV physical range.
BioSemi `.bdf`/BDF+ files are also accepted by the same reader.

### Writing

- `write_mat(...)` writes a v5 `.mat` (compatible with MATLAB R14+) using
  `scipy.io.savemat`.
- `write_edf(...)` writes an EDF file using `pyedflib`.

### The `MiData` container

Loaded signals are always wrapped in a `misleep.data.midata.MiData`:

| attribute  | type             | meaning                          |
|------------|------------------|----------------------------------|
| `signals`  | list of ndarray  | one 1-D array per channel        |
| `channels` | list of str      | channel names                    |
| `sf`       | list of float    | sampling frequency per channel   |
| `time`     | str              | acquisition time `YYYYMMDD-HH:MM:SS` |
| `duration` | int              | integer duration in seconds      |
| `n_channels` | int           | number of channels               |

## Annotation files

The GUI accepts `.txt`, `.json`, `.csv` and `.tsv` annotations.

### JSON

JSON mirrors the in-memory annotation object:

```json
{
  "sleep_state": [1, 1, 2, 3],
  "marker": [[1.5, "injection"]],
  "start_end": [[20, 30, "spindle"]],
  "state_map": {"1": "NREM", "2": "REM", "3": "Wake", "4": "Init"}
}
```

### CSV / TSV annotations

For per-second scoring, use a `state`, `state_code` or `sleep_state` column.
For interval scoring add `start` and `end` columns (seconds). Values may be
numeric codes or configured state names. Optional event rows use `type=marker`
with `time,label`, or `type=start_end` with `start,end,label`.

### MiSleep `.txt` format

The default annotation format is a human-readable text file:

```
READ ONLY! DO NOT EDIT!
4-INIT 3-Wake 2-REM 1-NREM
Save time: 2024-04-10 09:15:00
Acquisition time: 2024-04-09 18:00:00
==========Marker==========
, 30.5, 1, 30.5, 0, 1, injection
==========Start-End==========
, 50.0, 1, 70.0, 0, 1, spindle
==========Sleep stage==========
, 0, 1, 3599, 0, 1, NREM
, 3600, 1, 5399, 0, 2, REM
```

* **Marker** rows: `, <time_sec>, 1, <time_sec>, 0, 1, <label>`
* **Start-End** rows: `, <start_sec>, 1, <end_sec>, 0, 1, <label>`
* **Sleep stage** rows: `, <start_sec>, 1, <end_sec>, 0, <state_code>, <state_name>`

Loading handles the legacy variant where the first start index is 1
(one-based) as well as the current zero-based one.

### Bio-signal annotation

A tab-separated format whose first two lines are a header and whose
remaining lines contain the state name in the second column. States
`AW`/`QW` map to Wake (3), `NREM` to NREM (1) and `REMS` to REM (2);
each row is expanded to 4 seconds.

### The `MiAnnotation` container

Loaded annotations are wrapped in `misleep.data.annotation.MiAnnotation`:

| attribute    | type   | meaning                                  |
|--------------|--------|------------------------------------------|
| `sleep_state`| list   | one state code per second                |
| `marker`     | list   | `[[time, label], ...]`                   |
| `start_end`  | list   | `[[start, end, label], ...]`             |
| `state_map`  | dict   | code -> name mapping (default 1=NREM, 2=REM, 3=Wake, 4=Init) |
| `anno_length`| int    | annotation length in seconds             |

## Excel export

The **Transfer Result** tool produces an Excel workbook with three sheets:

* **Sleep state** — per-hour statistics: state code, state name, bout
  duration (s), plus per-hour NREM/REM/Wake/Init duration, bout count,
  average bout length and percentage. Two extra rows summarize the
  12 h light phase (`ZT0-ZT12`) and dark phase (`ZT12-ZT24`).
* **Start End** — all start-end events with timestamps.
* **Marker** — all markers with timestamps.
