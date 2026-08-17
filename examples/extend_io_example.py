# -*- coding: UTF-8 -*-
"""Extending MiSleep: register a custom signal reader.

This example shows how to plug a new file format into the MiSleep I/O
registry so that ``misleep.load_signal`` (and the GUI's file dialog)
can load it.
"""

from pathlib import Path

import numpy as np

from misleep.data import MiData
from misleep.io.base import register_signal_reader, load_signal


# ----------------------------------------------------------------------
# 1. Write a reader: ``func(path: str) -> MiData``
# ----------------------------------------------------------------------
def load_npy(path: str) -> MiData:
    """Load a trivial ``.npy`` format: a dict with signals/channels/sf/time."""
    data = np.load(path, allow_pickle=True).item()
    return MiData(
        signals=data["signals"],
        channels=data["channels"],
        sf=data["sf"],
        time=data["time"],
    )


def main():
    # 2. Register it for the ".npy" extension
    register_signal_reader(".npy", load_npy)

    # 3. Create a demo file and load it through the registry
    demo = Path("demo_midata.npy")
    np.save(demo, {
        "signals": [np.zeros(2560)],
        "channels": ["EEG"],
        "sf": [256.0],
        "time": "20240409-18:00:00",
    }, allow_pickle=True)

    midata = load_signal(demo)
    print("Loaded via registry:", midata)
    demo.unlink()


if __name__ == "__main__":
    main()
