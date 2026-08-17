# User guide — the MiSleep GUI

This guide describes the PySide6 desktop application. Launch it with
`python -m misleep` (or `misleep`).

## Overview

The main window follows the classic scoring workflow:

1. **Menu bar (top)** — the primary navigation (no icon-toolbar row):
   * **File** — Load Data, Load Annotation, Save Annotation, Save Data,
     Exit
   * **Tools** — Add Line, Event Detection (SWA, Spindle), Auto Stage
     (LightGBM, Transformer)
   * **Result** — State Spectral, Transfer Result
   * **Settings** — the in-application settings dialog (own menu)
   * **View** — expand/collapse the Data, Channels, Scoring and Display
     sidebar sections
   * **Help** — About
   The window starts **maximized**, so the signal area uses all the
   available width (no horizontal scrolling).
2. **Visualization area (center, the most important part)** — three
   stacked panels:
   * the **spectrogram** strip of the default channel,
   * the **signal area**: **one box per channel** (independent y scale),
     the figure fills the whole signal widget, the panels are tightly
     packed, and everything adapts when you resize the window,
   * the **hypnogram** at the bottom, with the **scroll bar** below.
3. **Tool area (right)** — one tidy **sidebar** with four collapsible
   sections: **Data** (paths, acquisition time; starts collapsed), the
   **Channels** list, **Scoring** and **Display**. Click a section header
   to expand/collapse it; the panel keeps a fixed width so the signal
   area stays dominant.

Usability details:

* The **mouse wheel** flips the signal window **only** when hovering over
  the signal or hypnogram panels; over the sidebar, tools or editors it
  never moves the signal, and it never changes spin/combo/date values
  either.
* Long display windows (30 min / 1 h) are **automatically downsampled**
  for fast redraws, and the x-axis tick density is reduced automatically.
* **Add Line** supports relative lines: enter a number N, choose
  *Standard deviation* (or *Mean*), and the line is placed at **N × SD**
  (or **N × Mean**) of the channel.
* The application and every dialog use the MiSleep logo as their icon.
* The interface is **high-DPI aware**: on large or scaled displays (e.g.
  2K/4K at 125–150 %) the plot canvases resize with the window and stay
  crisp.

## Preparation

### 1. Data file

MiSleep loads `.mat` and `.edf` files (see [Data formats](data_formats.md)).
A MATLAB `.mat` file should be a structure with:

```matlab
data.EEG      = [1 x N] double;   % channel data
data.EMG_DIFF = [1 x N] double;
data.channels = {'EEG', 'EMG_DIFF'};
data.sf       = [256, 256];       % sampling frequency per channel
data.time     = '20240409-18:00:00';
```

EDF is the European Data Format ([edfplus.info](https://edfplus.info/)) —
a standard format supported by most acquisition software.

### 2. Annotation file

Scoring is stored in a plain-text `.txt` file with three sections
(`==========Marker==========`, `==========Start-End==========`,
`==========Sleep stage==========`). You can create an empty file and let
MiSleep fill it in, or load an existing one (see
[Data formats](data_formats.md) for the exact layout).

### 3. Auto staging

If you want a quick start, load a data file, then use **Tools →
Auto Stage** (LightGBM or Causal Transformer) to generate an initial
scoring which you can then correct by hand.

## Loading data and annotations

Use the **File** menu, or the shortcuts:

* `Shift+D` — load data
* `Shift+A` — load annotation

After loading, MiSleep draws the data automatically.

## Visualization area

### Spectrogram strip

Shows the spectrogram (0.5–30 Hz by default) of the "default channel".
Change the default channel by selecting it in the channel list and
clicking **Default channel for spectrogram**. The **percentile** editor
controls the heat-map color scale.

### Signal area

Each channel gets **its own box** (independent y scale and amplitude
label), stacked below the spectrogram strip:

* **green dashed lines** every 5 seconds,
* **colored background** per sleep state (color and transparency
  configurable in **Help → Settings**),
* **red lines** for marker events (with their labels on top),
* **colored vertical lines** for start-end events (`-S`/`-E` markers),
* **horizontal reference lines** added via Tools → Add line.

The x-axis (seconds relative to the acquisition time) is shared; the
figure **fills the whole signal widget** and resizes with the window.
Navigation:

* scroll bar / click on the hypnogram — jump to a time,
* `Left`/`Right` — previous/next page,
* `Up`/`Down` — previous/next 5 s epoch,
* mouse wheel — page up/down.

### Channel list (Channels section)

* **▲ / ▼ arrow buttons** sit **horizontally in the same row as the
  spectrogram percentile box** (compact, 24×24) and move the selected
  channel up/down — the signal panel follows the new order immediately;
  channel names and data stay intact.
* To **rename** a channel, double-click its name in the list.
* **Show / Hide / Delete** — control which channels are displayed; delete
  removes them from the in-memory data.
* The sidebar keeps a **fixed, compact width** so the signal area stays
  dominant.

### Hypnogram

The per-second sleep state as a colored step plot (one color per state).
Click anywhere on it to jump to that time.

## Right-hand sidebar

### Data section

Shows the data path, annotation path, and acquisition time.

### Channels section

* **Show / Hide / Delete** — control which channels are displayed; delete
  removes them from the in-memory data.
* **Filter** — bandpass/highpass/lowpass/bandstop Butterworth filtering
  (`scipy.signal.filtfilt`); the filtered result is appended as a new
  channel (`<name>_<filter>_<freqs>`).
* **Scaler / Shift** — zoom (×0.9 / ×1.1 / custom factor) and vertical
  shift of selected channels for visualization.
* **Plot spectrum & spectrogram** — after selecting a start-end area
  (> 5 s) in the annotation area, opens the spectrum/spectrogram window
  for the selected channel.

### Scoring section

Three scoring modes (radio buttons) plus the **Marker list** / **Start-End
list** buttons which open a viewer of all already-labeled events:

* see every labeled marker / start-end event at a glance,
* **double-click** (or press *Jump to*) to jump to that location,
* **Add** a new event at the current time (label picked from your lists),
* **Delete** the selected event.

Scoring itself works as before:

* **Marker** — click on the signal to drop a marker at that time; the
  label picker lets you choose a marker name (or add new ones).
* **Start-End** — click twice to define a start-end interval with
  millisecond precision, then press `a` (or the **Label** button) to
  attach a label.
* **Save annotation** sits together with the **Marker list** and
  **Start-End list** buttons in one row (the lists let you see every
  labeled event, jump to it, add or delete).
* **Sleep state** — click twice to define an interval, then press one of
  the **state buttons** or the number key for that state (`1`–`9`, and
  `0` for state 10) to score it. The default has four states (1 NREM,
  2 REM, 3 Wake, 4 Init) whose buttons live in the Scoring section; add
  up to **10 states** in *Settings → Sleep states* and extra buttons
  appear below them, colored automatically.

Right-click removes markers / start-end selections.

### Display section

Jump to a specific time with the spin box or the date-time editor; choose
the display duration from the combo box (30 s – 1 h) or a custom value
(5 – 3600 s).

## Menu tools

### Tools

* **State Spectral** — per-state power spectra: choose a channel, time
  range, optional band-pass filtering, artifact rejection, Gaussian
  smoothing, window length (frequency resolution) and nfft. Results
  (spectra + Excel tables) are saved to a folder, one sheet per state,
  plus per-hour spectra when enabled.
* **Add Line** — horizontal reference lines (absolute value, or relative
  to the standard deviation / mean of a channel).
* **SWA detection** — slow-wave activity detection (0.5–4 Hz default)
  with state-specific amplitude thresholds; results are added to the
  annotation as `SWA` start-end events and can be exported to CSV.
* **Spindle Detection** — spindle detection (10–15 Hz default) with
  configurable thresholds; results are added as `Spindle` events.
* **Auto Stage (LightGBM)** — automatic staging with the packaged model.
  Choose the EEG and EMG channels, EEG electrode site (F/P) and mouse age
  group (adult / ado / P30).
* **Auto Stage (Causal Transformer)** — automatic staging with the
  PyTorch causal-transformer model (requires `misleep[transformer]`).

### Result

* **Transfer Result** — export per-hour and 12 h light/dark phase sleep
  statistics to an Excel workbook (sleep-state table, start-end events,
  markers).

### Help

* **View** — check/uncheck to expand or collapse the Data, Channels,
  Scoring and Display sidebar sections (same as clicking their headers).
* **About** — version and update info.
* **Settings** — opens the in-application settings dialog. Changes are
  **applied immediately** without restarting MiSleep:
  * *Sleep states* — edit state names and pick state background colors
    (click the color button to open the color picker),
  * *Colors* — start-end label colors (add/delete labels) and the marker /
    start-end line colors,
  * *Labels* — edit the marker and start-end label lists,
  * *Spectral* — default frequency range, FFT window length, nfft and
    Gaussian smoothing σ,
  * *General* — state background transparency, the **theme** (light/dark),
    the **spectrogram colormap**, and the default open path.
  An **"Open file…"** button opens the raw configuration file in your
  system editor for advanced edits (changes then require a restart).

## Saving

* `Ctrl+S` (or the **Save label** button) saves the annotation.
* Unsaved changes are indicated by an asterisk next to *Annotation path:*.
* **File → Save Data** exports the (optionally cropped, channel-selected)
  data to `.mat` or `.edf`.
* The annotation is **auto-saved every 5 minutes** when modified.
* On close, MiSleep asks whether to save or discard unsaved changes.

## Keyboard shortcuts

| Key | Action |
|-----|--------|
| `Shift+D` / `Shift+A` | load data / annotation |
| `Ctrl+S` | save annotation |
| `a` | append start-end label |
| `s` | open spectrum/spectrogram window |
| `1`–`6` | score the selected area with state 1–6 |
| `Ctrl+Shift+T` | toggle the light / dark theme |
| `Left` / `Right` | previous / next page |
| `Up` / `Down` | previous / next 5 s epoch |
| mouse wheel | page up / down |
