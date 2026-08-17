# -*- coding: UTF-8 -*-
"""Basic programmatic usage of MiSleep without the GUI.

Run from the repository root after ``pip install -e .``:

    python examples/basic_usage.py
"""

import matplotlib

matplotlib.use("Agg")  # headless backend (remove for interactive plotting)
import matplotlib.pyplot as plt

import misleep as ms
import numpy as np


def main():
    # 1. Build a synthetic MiData (normally you would load it):
    sf = 256.0
    t = np.arange(int(sf * 600)) / sf
    eeg = 2.0 * np.sin(2 * np.pi * 1.0 * t) + 0.2 * np.random.default_rng(0).standard_normal(t.size)
    emg = 0.3 * np.random.default_rng(1).standard_normal(t.size)

    midata = ms.MiData(
        signals=[eeg, emg],
        channels=["EEG", "EMG"],
        sf=[sf, sf],
        time="20240409-18:00:00",
        describe="synthetic example",
    )
    print(midata)

    # 2. Basic operations
    cropped = midata.crop([0, 300])
    eeg_only = midata.pick_chs(["EEG"])
    midata.filter(chans=["EEG"], btype="bandpass", low=0.5, high=30)
    print(f"After filter: {midata.n_channels} channels -> {midata.channels[-1]}")

    # 3. Spectral analysis
    freq, psd = ms.spectrum(cropped.signals[0], cropped.sf[0], band=[0.5, 30], relative=True)
    fig, ax = ms.plot_spectrum(freq, psd)
    fig.savefig("example_spectrum.png", dpi=150)
    print("Saved example_spectrum.png")

    # 4. Event detection
    swa = ms.SWA_detection(cropped.signals[0], cropped.sf[0], df=True)
    print("SWA detections:", 0 if swa is None else len(swa))

    # 5. Hypnogram from a synthetic annotation
    anno = ms.MiAnnotation(sleep_state=[1] * 200 + [2] * 100 + [3] * 100 + [1] * 200)
    fig, ax = ms.plot_hypno(anno.sleep_state)
    fig.savefig("example_hypnogram.png", dpi=150)
    print("Saved example_hypnogram.png")

    # 6. IO round trip
    import tempfile, os

    with tempfile.TemporaryDirectory() as tmp:
        mat_file = os.path.join(tmp, "out.mat")
        ms.write_mat(midata.signals, midata.channels, midata.sf, midata.time, mat_file)
        reloaded = ms.load_mat(mat_file)
        print(f"MAT round trip OK: {reloaded.channels}")

    # 7. Annotation export
    import datetime

    df, analyse_df, start_end_df, marker_df = ms.transfer_result(anno, datetime.datetime(2024, 4, 9, 18, 0, 0))
    print("Per-hour analysis:\n", analyse_df.head(3))


if __name__ == "__main__":
    main()
