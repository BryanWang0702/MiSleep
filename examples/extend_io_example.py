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
def load_xyz(path: str) -> MiData:
    """Load this example's safe, numeric format plus a fixed schema."""
    data = np.loadtxt(path, delimiter=",")
    return MiData(
        signals=[data[:, 0]],
        channels=["EEG"],
        sf=[256.0],
        time="20240409-18:00:00",
    )


def main():
    # 2. Register it for the ".npy" extension
    register_signal_reader(".xyz", load_xyz)

    # 3. Create a demo file and load it through the registry
    demo = Path("demo_midata.xyz")
    np.savetxt(demo, np.zeros((2560, 1)), delimiter=",")

    midata = load_signal(demo)
    print("Loaded via registry:", midata)
    demo.unlink()


if __name__ == "__main__":
    main()
