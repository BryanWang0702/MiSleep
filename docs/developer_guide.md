# Developer guide

This guide explains how MiSleep is organized and how to extend it. It is
aimed at contributors and at researchers who want to add their own file
formats, detectors or analysis steps.

## Architecture

MiSleep is split into small, single-responsibility modules with a stable
public API (see the [API reference](api_reference.md)):

```
src/misleep/
├── __init__.py          # public API re-exports (no heavy imports!)
├── __main__.py          # python -m misleep
├── data/                # data model (no scientific dependencies beyond numpy)
│   ├── midata.py        #   MiData: signals/channels/sf/time
│   └── annotation.py    #   MiAnnotation: sleep states, markers, start-end
├── io/                  # file I/O
│   ├── base.py          #   extension registry (readers/writers) + dispatch
│   ├── mat.py           #   .mat loader/saver (scipy + mat73)
│   ├── edf.py           #   .edf loader/saver (pyedflib)
│   └── annotation.py    #   MiSleep/bio annotation files + Excel export
├── preprocessing/       # signal processing
│   ├── filtering.py     #   Butterworth filters, mains noise
│   ├── artifacts.py     #   artifact rejection
│   ├── spectral.py      #   Welch spectrum, STFT spectrogram, band power
│   └── segment.py       #   per-state segmentation (crop_state_data)
├── analysis/            # science
│   ├── detection.py     #   SWA / spindle / artifact detection
│   ├── features.py      #   auto-staging feature extraction
│   ├── auto_stage.py    #   LightGBM auto staging
│   ├── models/          #   packaged LightGBM models (data)
│   └── transformer/     #   PyTorch causal transformer (lazy import!)
├── viz/                 # matplotlib plotting (no Qt dependency)
│   ├── signals.py
│   ├── spectral.py
│   └── hypnogram.py
├── gui/                 # PySide6 application
│   ├── app.py           #   entry points (show/main)
│   ├── main_window.py   #   main window
│   ├── spec_window.py   #   spectrum window
│   ├── dialogs.py       #   all dialogs
│   ├── workers.py       #   QThread-based I/O workers
│   ├── qt_utils.py      #   GUI helpers
│   ├── uis/             #   generated PySide6 UI modules (+ .ui sources)
│   └── resources/       #   Qt resources (logos)
├── config/              # config package
│   ├── __init__.py      #   load/save configuration
│   └── default_config.ini
├── logger.py            # logging setup
└── utils/               # pure helpers (annotation, time, entropy, misc)
```

### Design rules

1. **The GUI never owns the science.** All analysis lives in
   `misleep.analysis` / `misleep.preprocessing` and is unit-testable
   without Qt. The GUI only wires widgets to these functions.
2. **`misleep/__init__.py` stays light.** It does not import PySide6,
   PyTorch, or LightGBM, so `import misleep` works in any environment.
   Heavy dependencies are imported lazily inside the functions that need
   them.
3. **Data flows through `MiData`/`MiAnnotation`.** I/O converts files to
   and from these containers; the GUI and the analysis modules consume
   them. This keeps the rest of the code format-agnostic.
4. **Configuration is centralized.** Use `misleep.config.load_config()`
   instead of reading INI files yourself.

## Extending the I/O layer

New file formats can be registered either programmatically or through
entry points.

### Programmatic registration

```python
from misleep.data import MiData
from misleep.io.base import register_signal_reader, register_signal_writer

def load_my_format(path: str) -> MiData:
    ...  # parse `path` and return a MiData

def write_my_format(signals, channels, sf, time, file_path: str) -> None:
    ...

register_signal_reader(".xyz", load_my_format)
register_signal_writer(".xyz", write_my_format)

# Now the generic dispatchers know about it:
from misleep.io.base import load_signal, available_readers
midata = load_signal("recording.xyz")
```

### Entry-point registration (third-party packages)

Declare the reader in your package's `pyproject.toml`:

```toml
[project.entry-points."misleep.signal_readers"]
xyz = "mypackage.io:load_my_format"

[project.entry-points."misleep.signal_writers"]
xyz = "mypackage.io:write_my_format"
```

The functions must accept exactly the signatures shown above. MiSleep
discovers entry points through `importlib.metadata` on first use.

## Adding a detector

Detectors live in `misleep/analysis/detection.py` and follow a simple
contract: take a 1-D signal plus sampling frequency (and any thresholds),
return a list of detections or a pandas DataFrame.

```python
def my_detector(signal, sf, threshold=..., start_time_sec=0, df=False):
    ...
    return detections  # list of [start, end, ...] or DataFrame
```

Export it from `misleep/analysis/__init__.py` (and optionally from
`misleep/__init__.py`) and add a test under `tests/`. To surface it in
the GUI, add a dialog class in `misleep/gui/dialogs.py` and a menu action
in `main_window.py`.

## Adding a signal reader to the GUI file dialog

The GUI builds its open/save filters from the reader and writer registries.
Once an extension is registered, it appears automatically; no GUI edit is
needed. Entry-point names may be written as either `xyz` or `.xyz`.

## Opening files by double-click / command line

The GUI accepts file arguments: `misleep data.mat anno.txt` (see
`misleep/gui/app.py`). The main window exposes dialog-free
`open_data(path)` / `open_annotation(path)` methods that the CLI uses.

Windows file associations (double-click to open `.mat`/`.edf`) are
managed by `tools/install_file_associations.py`, which writes HKCU
registry keys (no admin rights), backs up the previous handlers to
`~/.misleep/file_assoc_backup.json`, and restores them with
`--uninstall`.

## The GUI and Qt

* The GUI is **PySide6-only** (Qt6). Never import `PyQt5`.
* Matplotlib is told to use the PySide6 bindings via the `QT_API`
  environment variable, which `misleep/gui/app.py` sets before anything
  else imports matplotlib.
* The `uis/*_ui.py` files are **generated** from the `uis/*.ui` sources
  with `pyside6-uic` (run `python tools/compile_ui.py` after editing a
  `.ui` file). Do not edit the generated files by hand.
* The Qt resources (`:/logo/...`) come from `resources/misleep.qrc`,
  compiled by `python tools/compile_resources.py`.

## Testing

```bash
pip install -e ".[gui,analysis,dev]"
pytest tests
```

* `tests/helpers.py` generates synthetic signals; fixtures in
  `tests/conftest.py` build a `MiData` and a `MiAnnotation`.
* Real-data round trips use the small example files in `tests/data/`.
* GUI tests run with `QT_QPA_PLATFORM=offscreen` and are skipped when
  PySide6 is missing.
* The transformer tests are skipped when PyTorch is missing.

## Packaging

* `pyproject.toml` follows PEP 621. Package data (models, checkpoints,
  config, resources, `.ui` sources) is declared under
  `[tool.setuptools.package-data]` and `MANIFEST.in` (for sdists).
* Optional dependency groups: `gui`, `analysis`, `transformer`, `full`,
  `dev`.
* The `misleep` console script is defined in `[project.scripts]`.
* Versioning: single source of truth is `misleep/__init__.py`
  (`__version__`); keep `pyproject.toml` and
  `config/default_config.ini` (`[gui] version`) in sync.

## Release checklist

1. Bump `__version__` in `src/misleep/__init__.py`, the version in
   `pyproject.toml` and the `[gui] version` in
   `config/default_config.ini`.
2. Update `CHANGELOG.md`.
3. Run `pytest tests`.
4. Rebuild the wheel and check the sdist contents:
   `python -m build` (or `pip wheel .`).
5. Tag and push; upload to PyPI with `twine upload dist/*`.
