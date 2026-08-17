# MiSleep v0.3 — Changelog

All notable changes to MiSleep are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- **GUI redesign**: the four right-side docks were replaced by one tidy
  **sidebar** with collapsible sections (named as before: Meta / Channel /
  Annotation / Time); the bottom **status bar was removed**; all sizes are
  DPI-aware (`pt`-based) with per-platform fonts, so the GUI scales
  cleanly on any screen.
- **Theme system**: light and dark themes driven by one palette that
  styles the Qt widgets *and* the matplotlib canvases together; toggle
  with `Ctrl+Shift+T` or *Settings → General → Theme* (persists in the
  user config). Dark mode also sets a matching QPalette so style-drawn
  elements (arrows, separators, calendar, state buttons) stay readable.
- **Data presentation**: hypnogram drawn as thick per-state blocks (easy
  to read on long recordings); every signal panel gets a visible frame;
  the spectrogram colormap stays `jet` by default (configurable in
  Settings).
- **Performance**: page flips are much faster — the whole-file
  spectrogram is cached per channel (sliced per window), the hypnogram
  base is cached and reused, signal axes are reused instead of recreated,
  state backgrounds are drawn as cheap rectangles, and dense traces are
  downsampled to 8k points.

## [0.3.0] — 2025

This is a major restructuring of the project (previously *MiSleep_v2*).

### Added

- **High-DPI support**: pass-through scale-factor rounding, per-monitor
  DPI awareness on Windows, and matplotlib canvases that resize with the
  window and fill their widgets in **device pixels** (so 2K/4K at
  125–150 % scaling is crisp and full-size, not a small corner plot).
- **In-application Settings dialog** (`Help → Settings`): edit sleep-state
  names & colors (with color-picker swatches), start-end label colors,
  marker / start-end label lists, spectral defaults and more. Changes are
  saved to the user config and **applied immediately** without restarting.
- **One box per channel** in the signal panel: every channel has its own
  axes with an independent scale; the figure fills the whole signal
  widget, follows window resizes, and the panels are tightly packed
  (no gaps between boxes).
- **Modern UI**: a flat stylesheet (`misleep/gui/style.py`) gives the
  whole application a clean, consistent look (white toolbar/menus, rounded
  controls, blue accent) without changing behaviour.
- **Icon toolbar removed** -- the menu bar is the primary navigation
  again (File / Tools / Result / View / Help), with no crowded icon row.
- **Channel reorder arrows moved** next to the spectrogram percentile box
  (they no longer sit beside the list), placed **horizontally in the same
  row** as the percentile spin, with a "Move:" notice label.
- **Compact right-side docks**: narrower minimum widths (Meta 270,
  Channel 250, Annotation 270, Time 200), sensible minimum heights and
  shorter labels, so the docks take less screen space.
- **Meta dock starts stacked**: it is collapsed to its title bar on
  launch with a ▼/▲ toggle to expand it (never removed, so it can always
  be restored); the window starts **maximized** to use all the width.
- **Settings** has its own menu-bar entry (no longer inside Help/About);
  the "Default channel for spectrogram" button shows its full name.
- **Sleep states**: the default configuration has **4 states** (1 NREM,
  2 REM, 3 Wake, 4 Init); up to **10 states** can be defined in
  *Settings → Sleep states* (add/remove buttons). The Annotation dock
  keeps its original 1-4 buttons and adds colored buttons below them for
  extra states, and the number keys `1`-`9` (plus `0` for state 10) label
  the selected area.
- **Fast long-window display**: 30 min / 1 h windows are downsampled to
  ~60k points per channel and the x-axis ticks are auto-reduced, so
  scrolling long recordings stays smooth.
- **Marker list / Start-End list** buttons now sit in the same row as
  *Save annotation* (no gap between them).
- **Thinner inputs**: spin boxes and combos in the docks are narrower
  (64 px spins, 100 px combos) so the docks take less width.
- **Initial dock heights**: Meta starts stacked (24 px), Annotation and
  Time are small, and the **Channel dock is the longest** for the best
  display; the Meta dock expands to a comfortable height when toggled.
- **Mouse-wheel scope**: flipping pages with the wheel works only over
  the signal / hypnogram panels; over docks, tools or editors the wheel
  never moves the signal window (and never edits spin/combo/date values).
- **Add Line fixed**: relative lines now honour the entered number --
  ``N`` x Standard deviation (or x Mean) of the channel instead of always
  placing the line at 1 x SD.
- **Menu bar restored and reorganized** on top (File with Save
  Annotation + Exit, Tools, Result, View with dock toggles, Help with
  Settings).
- **Meta dock back on the right** with balanced initial sizes for the
  Meta / Channel / Annotation / Time docks.
- **App & dialog icons** use the MiSleep logo from the packaged Qt
  resources (application icon, main window and all dialogs).
- **Workflow toolbar** at the top: Open Data / Open Anno / Save, SWA /
  Spindle / Auto Stage / Auto Stage TF, State Spectral / Add Line,
  Transfer Result / Save Data, Settings / About, plus dock toggles; a
  status bar shows the loaded recording.
- **Mouse-wheel safety**: the wheel never changes spin/combo/date values;
  hovering over the signal or hypnogram panels scrolls the window
  (previous/next page).
- **Event lists**: "Marker list" and "Start-End list" buttons in the
  Annotation dock open a viewer of all labeled events -- double-click to
  jump, plus add and delete.
- **Channel reordering via buttons**: drag & drop was removed; the
  channel list now has **▲ / ▼ arrows right beside the list** that move
  the selected channel and update the signal panel immediately
  (`MiData.reorder_channels`). Renaming is a double-click and never
  conflicts with reordering.
- **Scrollable dock widgets**: when the window is too small for a dock's
  controls, its contents scroll instead of clipping; the docks keep the
  original right-side arrangement and a **View** menu toggles each one.
- **Modern packaging**: `pyproject.toml` (PEP 621), `src/` layout,
  `misleep` console-script entry point, `python -m misleep` entry point,
  optional dependency groups (`gui`, `analysis`, `transformer`, `full`, `dev`).
- **PySide6 (Qt6) GUI** replacing PyQt5, for cross-platform support on
  Windows, macOS and Linux.
- **Modular architecture**: separated `data` (MiData/MiAnnotation),
  `io` (MAT/EDF/annotation + plugin registry), `preprocessing`,
  `analysis`, `viz` and `gui` modules.
- **Extensible I/O registry**: `misleep.io.base.register_signal_reader` /
  `register_signal_writer` plus entry-point based discovery
  (`misleep.signal_readers` / `misleep.signal_writers`).
- **Per-user configuration**: the config is now read from
  `~/.misleep/misleep_config.ini` on top of bundled defaults instead of a
  CWD-relative `./misleep/config.ini`.
- **Proper logging**: logs to the console and to a rotating file under
  `~/.misleep/logs/misleep.log` (no more CWD-relative `logger.log`).
- **Package data**: the LightGBM models (`.pkl`) and the
  CausalTransformer checkpoint (`.pt`) are shipped inside the package and
  located with `importlib.resources` — no CWD-relative model paths.
- **Lazy heavy imports**: importing `misleep` or `misleep.gui` no longer
  requires PyTorch / PySide6; only the corresponding feature does.
- **Tests**: a pytest suite with synthetic-data fixtures and real-data
  round-trip tests (`tests/`).
- **Documentation**: user guide, data-format docs, config reference, API
  reference and a developer guide under `docs/`.
- **Examples**: runnable scripts under `examples/`.
- **Tooling**: `tools/compile_ui.py` and `tools/compile_resources.py` to
  regenerate the PySide6 UI modules and Qt resources.

### Changed

- Class names in the GUI were renamed to PascalCase
  (`MainWindow`, `LabelDialog`, `AboutDialog`, ...); a `main_window`
  alias is kept for compatibility.
- The channel move arrows (▲/▼), the *Marker list* / *Start-End list*
  buttons and the extra sleep-state button panel are now **declared in
  `main_window.ui`** (and wired in `init_qt`) instead of being injected
  into the dock layouts at runtime; this removes the fragile
  `layout.itemAt(...)` grid-patching and keeps the visual result
  identical. Fixes the stray UI text ("Anntation" title, "UP" button,
  "Plot spectrum and spectrogram", "Annotation" label).
- MAT files are now written with `scipy.io.savemat` (v5) instead of the
  unmaintained `hdf5storage` package; reading of old MATLAB / MiSleep
  files (v5, v7, v7.3, python-saved) is unchanged.
- `scipy.integrate.simps` replaced with `simpson`.
- `matplotlib` colormap access uses `plt.get_cmap` (removed legacy API).
- The `utils/signals.py` module was split into `preprocessing/filtering.py`
  and `utils/` helpers; `misleep.signal_filter` remains available.
- The transformer package moved to `misleep/analysis/transformer/`
  (from `auto_stage_causal_transformer/llm_eeg`).

### Fixed

- Annotation saving no longer crashes on integer seconds (ms formatting).
- EDF writing uses header keys accepted by current pyedflib versions.
- Hypnogram redraw no longer crashes after the axes are recreated.
- `MiAnnotation` always exposes `marker`/`start_end` (empty lists when
  not provided).

[0.3.0]: https://github.com/BryanWang0702/MiSleep/releases/tag/v0.3.0
