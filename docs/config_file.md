# Configuration file

MiSleep is configured through an INI file. A **default configuration**
ships with the package; on first launch a **user configuration** is
created at:

| Platform | Path |
|----------|------|
| Windows | `%USERPROFILE%\.misleep\misleep_config.ini` |
| macOS / Linux | `~/.misleep/misleep_config.ini` |

Set `MISLEEP_DATA_DIR` to place both the user configuration and logs in
another writable directory. This is useful for portable installations,
managed workstations and automated tests.

User settings override the bundled defaults, so package upgrades never
wipe your personal settings. Open the user file from the GUI via
**Help → Config**; changes take effect after restarting MiSleep.

## Sections

### `[gui]`

| key | default | meaning |
|-----|---------|---------|
| `version` | `v0.3.0` | displayed in the About dialog |
| `updatetime` | `2025/01/01` | displayed in the About dialog |
| `marker` | `['half_signal', 'first REM', ...]` | marker label list (label picker) |
| `startend` | `['high_theta', 'REM', ...]` | start-end label list (label picker) |
| `statemap` | `{"1": "NREM", "2": "REM", "3": "Wake", "4": "INIT", ...}` | state code -> name mapping (JSON) |
| `statecolor` | `{"1": "orange", ...}` | state code -> color (JSON) |
| `startendcolor` | `{"NREM": "orange", ...}` | start-end label -> color (JSON) |
| `statecolorbgalpha` | `0.1` | transparency of the sleep-state background |
| `markerlinecolor` | `red` | color of marker lines |
| `startendlinecolor` | `blue` | color of start-end lines |
| `freq_range` | `[0.5, 30]` | frequency range for the spectrogram / spectrum |
| `openpath` | `.` | default folder for file dialogs (updated automatically) |

### `[spec]`

| key | default | meaning |
|-----|---------|---------|
| `win_length_sec` | `10.0` | default FFT window length (s) for spectra |
| `nfft_sec` | `10.0` | default nfft (s) for spectra |
| `gaussian_sigma` | `1.0` | default Gaussian smoothing sigma |

## Example

```ini
[gui]
version = v0.3.0
updatetime = 2025/01/01
marker = ['half_signal', 'first REM', 'WindEEG', 'W-R', 'maker']
startend = ['high_theta', 'REM', 'Wake', 'Spindle', 'SWA', 'start end label', 'start end label']
statemap = {"1": "NREM", "2": "REM", "3": "Wake", "4": "INIT", "5": "IS", "6": "MicroArousal"}
statecolor = {"1": "orange", "2": "skyblue", "3": "red", "4": "white", "5": "green", "6": "pink"}
startendcolor = {"NREM": "orange", "REM": "skyblue", "Wake": "red"}
statecolorbgalpha = 0.1
markerlinecolor = "red"
startendlinecolor = "blue"
freq_range = [0.5, 30]
openpath = .

[spec]
win_length_sec = 10.0
nfft_sec = 10.0
gaussian_sigma = 1.0
```

## Programmatic use

```python
from misleep.config import load_config, save_config, user_config_path

cfg = load_config()                       # defaults + user overrides
print(cfg["gui"]["statemap"])

cfg.set("gui", "statecolorbgalpha", "0.2")
save_config(cfg)                          # written to the user file

print(user_config_path())                 # where the user file lives
```
