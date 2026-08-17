# API reference

This page documents the public API of MiSleep. Everything listed here is
importable from the top-level `misleep` package unless stated otherwise.

## Data model

### `misleep.data.MiData`

The in-memory signal container.

```python
from misleep.data import MiData

md = MiData(signals, channels, sf, time, describe=None)
```

| member | description |
|--------|-------------|
| `signals` | list of 1-D numpy arrays (one per channel) |
| `channels` | list of channel names |
| `sf` | list of sampling frequencies |
| `time` | acquisition time string `YYYYMMDD-HH:MM:SS` |
| `describe` | optional free-text description |
| `duration` (property) | integer duration in seconds |
| `n_channels` (property) | number of channels |
| `add(signal, channel, sf)` | append a channel |
| `delete(channel)` | remove a channel by name |
| `rename_channels(mapping)` | rename channels in place |
| `filter(chans, btype, low, high)` | filter channels, append results |
| `differential(chan1, chan2)` | add `chan1 - chan2` as a new channel |
| `crop(time_period)` | return a cropped copy (`[start, end]` seconds) |
| `pick_chs(ch_names)` | return a copy with selected channels |
| `get_channel_index(channel)` | index of a channel by name |

### `misleep.data.MiAnnotation`

The scoring container.

```python
from misleep.data import MiAnnotation

anno = MiAnnotation(sleep_state, marker=None, start_end=None, state_map=None)
```

Default state map: `{1: 'NREM', 2: 'REM', 3: 'Wake', 4: 'Init'}`.

| member | description |
|--------|-------------|
| `sleep_state` (property) | per-second state codes (list) |
| `marker` (property) | `[[time, label], ...]` |
| `start_end` (property) | `[[start, end, label], ...]` |
| `state_map` (property) | code -> name mapping |
| `state_names` (property) | sorted state names |
| `anno_length` (property) | length in seconds |

## Input / output (`misleep.io`)

### Signals

* `load_mat(data_path)` → `MiData | None` — load a MATLAB `.mat` file
  (v5/v7 via scipy, v7.3 via mat73; MATLAB- or python-saved).
* `load_edf(data_path)` → `MiData` — load an EDF/EDF+ file.
* `write_mat(signals, channels, sf, time, mat_file=None)` — write a v5
  `.mat` file.
* `write_edf(signals, channels, sf, time, edf_file=None)` — write an EDF
  file.
* `load_signal(path)` → `MiData` — dispatch by file extension.
* `write_signal(midata, path)` — dispatch by file extension.
* `available_readers()` / `available_writers()` → list of extensions.
* `register_signal_reader(ext, func)` / `register_signal_writer(ext, func)`
  — register a custom format (see
  [developer guide](developer_guide.md#extending-the-io-layer)).

### Annotations

* `load_misleep_anno(file_path, state_map=None)` → `MiAnnotation`.
* `save_misleep_anno(mianno, midata, file_path)` → `bool`.
* `load_bio_anno(file_path)` → `MiAnnotation` (bio-signal tab format).
* `transfer_result(mianno, ac_time)` → `(df, analyse_df, start_end_df, marker_df)`
  — per-hour and light/dark phase sleep statistics.

## Preprocessing (`misleep.preprocessing`)

* `signal_filter(data, sf=256, btype='lowpass', low=0.5, high=30)` →
  `(filtered, fname)` — zero-phase Butterworth filter.
* `filter_power_line_noise(data, sf, noise_band='50-100-150')` → ndarray
  — mains noise removal.
* `z_score(signal)` → ndarray — `(x - mean) / std`.
* `reject_artifact(signal, sf=None, threshold=2)` → ndarray — epoch-based
  artifact rejection.
* `spectrum(signal, sf, band=[0.5, 30], relative=True, win_sec=1, nfft=None,
  gaussian_sigma=None)` → `(freq, psd)` — Welch PSD.
* `spectrogram(signal, sf, band=[0.5, 30], step=0.2, win_sec=2, norm=False,
  nfft=None)` → `(f, t, Sxx)` — STFT spectrogram.
* `band_power(psd, freq, bands, relative=False)` → dict — band powers
  (composite Simpson rule).

## Analysis (`misleep.analysis`)

### Event detection

* `SWA_detection(signal, sf, freq_band=[0.5, 4], amp_threshold=(75,),
  df=False, start_time_sec=0)` → list | DataFrame | None — slow-wave
  detection with per-wave features (times, amplitudes, PTP, slope,
  frequency).
* `spindle_detection(signal, sf, freq_band=[10, 15], start_time_sec=0,
  std_thresh=None, duration_thresh=None)` → list | None — spindle
  detection via spectrogram power thresholds.
* `artifact_detection(signal)` — placeholder.

### Feature extraction

* `split_window_data(data, sf, state, window_length=20, stride_length=5)`
  → list of `[window, state]`.
* `get_data_features(data, sf, data_format='EEG')` → DataFrame — the
  feature set used for auto staging.
* `self_zscore(feature, quantile=0.95)` — quantile-clipped z-score.

### Automatic staging

* `auto_stage_gbm(EEG, EMG, label, sf, EEG_channel='F', mouse_age='adult')`
  → list of per-second states — LightGBM auto staging.
* `result_constraints(pred_prob)` → list — smooth/constrain raw model
  probabilities into state labels.
* `model_path(mouse_age='adult', EEG_channel='F')` → Path — packaged
  LightGBM model path.
* `misleep.analysis.transformer.auto_stage_llm(EEG, EMG, label=None,
  config=None)` → list — transformer auto staging (requires torch).
* `misleep.analysis.transformer.AutoStageConfig` — dataclass of
  preprocessing/finetune/output options.
* `misleep.analysis.transformer.default_checkpoint_path()` → Path —
  packaged transformer checkpoint path.

## Visualization (`misleep.viz`)

* `plot_signals(signals, sf=None, ch_names=None)` → `(fig, axs)`.
* `plot_spectrum(f, p)` → `(fig, ax)`.
* `plot_spectrogram(f, t, Sxx, percentile=100, band=None, color_bar=False)`
  → `(fig, ax)`.
* `plot_hypno(sleep_state, state_map=None, time_range=[0, -1])` → `(fig, ax)`.

## Configuration & logging

* `misleep.config.load_config(path=None)` → `configparser.ConfigParser` —
  merged defaults + user config.
* `misleep.config.save_config(config, path=None)` → Path.
* `misleep.config.user_config_path()` → Path.
* `misleep.config.default_config_path()` → Path.
* `misleep.logger.logger` — the shared `logging.Logger`.

## GUI (`misleep.gui`)

* `misleep.gui.show()` — start the GUI (blocking).
* `misleep.gui.main()` — console-script entry point.
* `misleep.gui.main_window.MainWindow` — the main window class.
* `misleep.gui.spec_window.SpecWindow` — spectrum/spectrogram window.
* `misleep.gui.dialogs.*` — the dialog classes.

## Backward compatibility

The following old import paths still work:

* `misleep.io.base.MiData` / `MiAnnotation`
* `misleep.gui.main_window.main_window` (alias of `MainWindow`)
* top-level `misleep.signal_filter`, `misleep.spectrogram`,
  `misleep.band_power`, `misleep.spectrum`, `misleep.load_mat`,
  `misleep.load_edf`, `misleep.crop_state_data` etc.
