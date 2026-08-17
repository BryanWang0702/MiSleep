# -*- coding: UTF-8 -*-
"""Tests for the I/O module: MAT/EDF round trips and annotation I/O."""

import datetime

import numpy as np
import pytest

from misleep.io import (
    load_edf,
    load_misleep_anno,
    load_signal,
    save_misleep_anno,
    transfer_result,
    write_edf,
    write_mat,
)
from misleep.io.base import available_readers, available_writers, write_signal
from misleep.io.mat import load_mat

DATA_DIR = __import__("pathlib").Path(__file__).parent / "data"


def _pyedflib_available():
    try:
        import pyedflib  # noqa: F401

        return True
    except ImportError:
        return False


def test_registry():
    assert ".mat" in available_readers()
    assert ".edf" in available_readers()
    assert ".mat" in available_writers()
    assert ".edf" in available_writers()


def test_load_signal_dispatch():
    midata = load_signal(DATA_DIR / "10mins_example_mat.mat")
    assert midata.n_channels >= 1


def test_unsupported_extension(tmp_path):
    bad = tmp_path / "data.xyz"
    bad.write_bytes(b"")
    with pytest.raises(ValueError):
        load_signal(bad)


def test_mat_round_trip(tmp_path, midata):
    out = tmp_path / "roundtrip.mat"
    write_mat(midata.signals, midata.channels, midata.sf, midata.time, str(out))
    loaded = load_mat(str(out))
    assert loaded.channels == midata.channels
    assert loaded.sf == midata.sf
    assert loaded.time == midata.time
    assert loaded.duration == midata.duration
    np.testing.assert_allclose(loaded.signals[0], midata.signals[0], atol=1e-8)


def test_load_real_mat_file():
    midata = load_mat(str(DATA_DIR / "10mins_example_mat.mat"))
    assert midata is not None
    assert len(midata.signals) == len(midata.channels)
    assert all(s > 0 for s in midata.sf)


@pytest.mark.skipif(not _pyedflib_available(), reason="pyedflib not installed")
def test_edf_round_trip(tmp_path, midata):
    out = tmp_path / "roundtrip.edf"
    write_edf(midata.signals, midata.channels, midata.sf, midata.time, str(out))
    loaded = load_edf(str(out))
    assert loaded.channels == midata.channels
    assert loaded.duration == midata.duration
    # EDF stores physical values with 16-bit resolution, so allow some
    # quantization error on the reconstructed signal.
    max_err = np.abs(loaded.signals[0] - midata.signals[0]).max()
    assert max_err < 5.0


def test_write_signal_dispatch(tmp_path, midata):
    out = tmp_path / "dispatched.mat"
    write_signal(midata, str(out))
    assert out.exists()


def test_misleep_anno_round_trip(tmp_path, mianno, midata):
    out = tmp_path / "anno.txt"
    assert save_misleep_anno(mianno, midata, str(out)) is True
    loaded = load_misleep_anno(str(out))
    assert loaded.anno_length == mianno.anno_length
    assert loaded.sleep_state == mianno.sleep_state
    assert loaded.marker == mianno.marker
    assert loaded.start_end == mianno.start_end


def test_load_misleep_anno_empty(tmp_path):
    empty = tmp_path / "empty.txt"
    empty.write_text("")
    with pytest.raises(AssertionError):
        load_misleep_anno(str(empty))


def test_transfer_result(mianno):
    ac_time = datetime.datetime(2024, 4, 9, 18, 0, 0)
    df, analyse_df, start_end_df, marker_df = transfer_result(mianno, ac_time)
    assert "start_time" in df.columns
    assert "NREM_duration" in analyse_df.columns
    assert "label" in start_end_df.columns
    assert "timestamp" in marker_df.columns
    assert len(marker_df) == 1  # one marker
