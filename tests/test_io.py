# -*- coding: UTF-8 -*-
"""Tests for the I/O module: MAT/EDF round trips and annotation I/O."""

import datetime

import numpy as np
import pytest

from misleep.io import (
    load_annotation,
    load_csv,
    load_edf,
    load_misleep_anno,
    load_npy,
    load_npz,
    load_signal,
    save_misleep_anno,
    transfer_result,
    write_edf,
    write_mat,
    write_npz,
)
from misleep.io.base import (
    available_readers,
    available_writers,
    register_signal_reader,
    write_signal,
)
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
    for extension in (".npy", ".npz", ".csv", ".tsv", ".bdf"):
        assert extension in available_readers()
    assert ".npz" in available_writers()
    register_signal_reader("DUMMY", lambda path: None)
    assert ".dummy" in available_readers()


def test_numpy_npz_round_trip(tmp_path, midata):
    out = tmp_path / "signals.npz"
    write_npz(midata.signals, midata.channels, midata.sf, midata.time, out)
    loaded = load_npz(out)
    assert loaded.channels == midata.channels
    assert loaded.sf == midata.sf
    assert loaded.time == midata.time
    np.testing.assert_allclose(loaded.signals[0], midata.signals[0])

    matrix_out = tmp_path / "matrix.npz"
    np.savez(matrix_out, signals=np.arange(40).reshape(20, 2),
             channels=np.array(["A", "B"]), sf=np.array([10, 10]),
             time=np.array("20240409-18:00:00"), channel_axis=np.array(1))
    matrix = load_npz(matrix_out)
    assert matrix.channels == ["A", "B"]
    assert matrix.duration == 2


def test_numpy_npy_with_sidecar(tmp_path):
    out = tmp_path / "signals.npy"
    np.save(out, np.arange(40, dtype=float).reshape(2, 20))
    out.with_suffix(".npy.json").write_text(
        '{"sf": 10, "channels": ["EEG", "EMG"], '
        '"time": "20240409-18:00:00", "channel_axis": 0}',
        encoding="utf-8",
    )
    loaded = load_npy(out)
    assert loaded.channels == ["EEG", "EMG"]
    assert loaded.duration == 2


def test_numpy_npy_requires_sampling_frequency(tmp_path):
    out = tmp_path / "signals.npy"
    np.save(out, np.zeros(20))
    with pytest.raises(ValueError, match="Sampling frequency"):
        load_npy(out)


def test_csv_signal_infers_sampling_frequency(tmp_path):
    out = tmp_path / "signals.csv"
    out.write_text("time,EEG,EMG\n0,1,2\n0.5,3,4\n1.0,5,6\n1.5,7,8\n",
                   encoding="utf-8")
    loaded = load_csv(out)
    assert loaded.channels == ["EEG", "EMG"]
    assert loaded.sf == [2.0, 2.0]
    assert loaded.duration == 2


def test_json_and_csv_annotations(tmp_path):
    json_path = tmp_path / "anno.json"
    json_path.write_text(
        '{"sleep_state": [1, 1, 2], "marker": [[1.5, "note"]], '
        '"start_end": [], "state_map": {"1": "NREM", "2": "REM"}}',
        encoding="utf-8",
    )
    json_anno = load_annotation(json_path)
    assert json_anno.sleep_state == [1, 1, 2]
    assert json_anno.marker == [[1.5, "note"]]

    csv_path = tmp_path / "anno.csv"
    csv_path.write_text("start,end,state\n0,2,NREM\n2,4,REM\n", encoding="utf-8")
    csv_anno = load_annotation(csv_path)
    assert csv_anno.sleep_state == [1, 1, 2, 2]


def test_epoch_tsv_annotations(tmp_path):
    """BIDS onset/duration/stage and epoch [second, label] tables."""
    # BIDS-style events.tsv
    bids = tmp_path / "events.tsv"
    bids.write_text("onset\tduration\tstage\n0\t4\t1\n4\t4\t2\n8\t4\t3\n",
                    encoding="utf-8")
    anno = load_annotation(bids)
    assert anno.sleep_state[:12] == [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3]

    # headerless 3 columns: epoch index, epoch second, epoch label
    three = tmp_path / "three.tsv"
    three.write_text("0\t0\t1\n1\t4\t2\n", encoding="utf-8")
    anno3 = load_annotation(three)
    assert anno3.sleep_state[:8] == [1, 1, 1, 1, 2, 2, 2, 2]

    # headerless 2 columns: epoch second, epoch label (no index column)
    two = tmp_path / "two.tsv"
    two.write_text("0\t1\n10\t3\n", encoding="utf-8")
    anno2 = load_annotation(two)
    assert anno2.sleep_state[:10] == [1] * 10
    assert anno2.sleep_state[10:15] == [3] * 5

    # header [epoch, second, label]
    hdr = tmp_path / "hdr.tsv"
    hdr.write_text("epoch\tsecond\tlabel\n0\t0\tNREM\n1\t5\tREM\n", encoding="utf-8")
    anno4 = load_annotation(hdr, state_map={1: "NREM", 2: "REM", 3: "Wake", 4: "Init"})
    assert anno4.sleep_state[:5] == [1] * 5
    assert anno4.sleep_state[5:10] == [2] * 5


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
