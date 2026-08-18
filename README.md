# MiSleep

**MiSleep** is an open-source Python toolbox for **mice sleep EEG/EMG**
visualization, scoring, and analysis.

![logo](src/misleep/gui/resources/entire_logo.png)

The name *MiSleep* comes from "**Mi**ce **Sleep**" and sounds like
"**my sleep**".

| | |
|---|---|
| License | BSD 3-Clause |
| Python | 3.9 – 3.14 |
| GUI toolkit | PySide6 (Qt6) — Windows, macOS, Linux |
| Documentation | [https://bryanwang.cn/MiSleep/](https://bryanwang.cn/MiSleep/) |

---

## Features

- **Cross-platform desktop GUI** built on **PySide6** (Qt6). Works on
  Windows, macOS and Linux without any platform-specific code.
- **Flexible data input** — load MATLAB, EDF/EDF+, BDF, NumPy NPY/NPZ,
  CSV and TSV recordings; JSON/CSV/TSV annotation imports are also built in.
- **Full scoring workflow** — per-second sleep state scoring (NREM / REM /
  Wake / Init), single time-point markers, start-end events, hypnogram,
  spectrogram and per-state spectral analysis.
- **Event detection** — slow-wave activity (SWA) and sleep spindle
  detection with state-specific thresholds.
- **Automatic sleep staging** — a LightGBM classifier (trained on
  time- and frequency-domain features) and an optional PyTorch
  causal-transformer model.
- **Analysis export** — per-hour and 12 h light/dark phase sleep
  statistics exported to Excel.
- **Clean, modular architecture** — data, I/O, preprocessing, analysis,
  visualization and GUI are separate modules with a stable public API and
  plugin-friendly extension points (see the
  [developer guide](docs/developer_guide.md)).

## Installation

```bash
# Core package (data, I/O, preprocessing, analysis, visualization)
pip install misleep

# With the PySide6 GUI (recommended for most users)
pip install "misleep[gui]"

# With everything, including the LightGBM auto-staging model
pip install "misleep[full]"

# For development / contributing
git clone https://github.com/BryanWang0702/MiSleep.git
cd misleepv3
pip install -e ".[gui,analysis,dev]"
```

> **Note on PyTorch:** the causal-transformer auto-staging model requires
> `torch`, which is not available on every platform. Install it
> separately with `pip install "misleep[transformer]"`.

## Quick start

### Launch the GUI

```bash
python -m misleep
# or, after installation:
misleep
```

### Open files directly (command line)

```bash
misleep data.mat                # open a recording
misleep data.mat anno.txt       # open a recording + its annotation
misleep --data data.edf --anno anno.txt
python -m misleep data.mat      # same via the module
```

### Open files by double-clicking (Windows)

Register MiSleep as the handler for your recording files:

```bash
python tools/install_file_associations.py
```

After that, **double-clicking a `.mat` or `.edf` file opens it in MiSleep**
(no console window). Annotation `.txt` files get an **"Open with MiSleep"**
right-click menu item without changing their default handler. The previous
`.mat`/`.edf` handlers are backed up automatically and restored with:

```bash
python tools/install_file_associations.py --uninstall
```

On macOS/Linux, run the same script for instructions (or open files from
the command line as shown above).

### Use the library

```python
import misleep as ms

# Load a recording
midata = ms.load_signal("data.npz")     # MAT, EDF/BDF, NPY/NPZ, CSV or TSV

# Inspect it
print(midata.channels, midata.sf, midata.duration)

# Preprocess
midata.filter(chans=["EEG"], btype="bandpass", low=0.5, high=30)
nrem, rem, wake, init = ms.crop_state_data(midata, mianno)

# Analyze
freq, psd = ms.spectrum(midata.signals[0], midata.sf[0])
swa = ms.SWA_detection(midata.signals[0], midata.sf[0], df=True)

# Plot
fig, ax = ms.plot_hypno(mianno.sleep_state)
```

See [docs/getting_started.md](docs/getting_started.md) and the
[examples](examples/) folder for more.

## Project layout

```
misleepv3/
├── pyproject.toml            # modern packaging (PEP 621)
├── src/misleep/
│   ├── data/                 # data model: MiData, MiAnnotation
│   ├── io/                   # input/output: MAT, EDF, annotations (+ plugin registry)
│   ├── preprocessing/        # filtering, artifact rejection, spectral analysis
│   ├── analysis/             # detection, feature extraction, auto staging
│   ├── viz/                  # matplotlib plotting (signals, spectra, hypnograms)
│   ├── gui/                  # PySide6 desktop application
│   ├── utils/                # shared helpers
│   ├── config.py             # INI configuration handling
│   └── logger.py             # logging setup
├── tests/                    # pytest suite
├── docs/                     # user + developer documentation
├── examples/                 # runnable examples
└── tools/                    # UI/resource compilation scripts
```

## Documentation

- [Getting started](docs/getting_started.md) — installation and first steps
- [User guide](docs/user_guide.md) — the GUI in detail
- [Data formats](docs/data_formats.md) — how data and annotations are stored
- [Configuration](docs/config_file.md) — the `config.ini` reference
- [API reference](docs/api_reference.md) — full API documentation
- [Developer guide](docs/developer_guide.md) — architecture and how to extend MiSleep
- [Changelog](CHANGELOG.md)

## Citing MiSleep

If you use this software in your research, please cite it as:

> Xueqiang Wang. (2024). BryanWang0702/MiSleep. Zenodo.
> https://doi.org/10.5281/zenodo.14511905

## License

BSD 3-Clause. See [LICENSE](LICENSE).
