# -*- coding: UTF-8 -*-
"""Automatic sleep staging (LightGBM) without the GUI.

Run from the repository root after ``pip install -e '.[analysis]'``:

    python examples/auto_stage_example.py
"""

import numpy as np

from misleep.analysis.auto_stage import auto_stage_gbm
from misleep.io.mat import load_mat


def main():
    # Replace with your own data file (EEG + EMG channels)
    # midata = load_mat("path/to/your.mat")
    # eeg_idx = midata.channels.index("EEG")
    # emg_idx = midata.channels.index("EMG")
    # eeg, emg, sf = midata.signals[eeg_idx], midata.signals[emg_idx], midata.sf[eeg_idx]

    # Synthetic demo data
    sf = 256.0
    t = np.arange(int(sf * 600)) / sf
    rng = np.random.default_rng(0)
    eeg = 2.0 * np.sin(2 * np.pi * 1.0 * t) + 0.2 * rng.standard_normal(t.size)
    emg = 0.3 * rng.standard_normal(t.size)

    # EEG site (F or P) and mouse age category select which model is used
    pred_label = auto_stage_gbm(EEG=eeg, EMG=emg, label=[4] * 600, sf=sf,
                                EEG_channel="F", mouse_age="adult")

    print(f"Predicted {len(pred_label)} seconds of sleep states:")
    n_nrem = pred_label.count(1)
    n_rem = pred_label.count(2)
    n_wake = pred_label.count(3)
    print(f"  NREM: {n_nrem}s, REM: {n_rem}s, Wake: {n_wake}s")


if __name__ == "__main__":
    main()
