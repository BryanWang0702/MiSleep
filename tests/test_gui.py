# -*- coding: UTF-8 -*-
"""Tests for the public package API and the GUI (offscreen)."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_API", "pyside6")

import pytest  # noqa: E402


def _pyside6_available():
    try:
        import PySide6  # noqa: F401

        return True
    except ImportError:
        return False


def test_public_api():
    import misleep

    assert misleep.__version__ == "0.3.0"
    for name in [
        "MiData",
        "MiAnnotation",
        "load_mat",
        "write_mat",
        "load_edf",
        "write_edf",
        "load_npy",
        "load_npz",
        "load_csv",
        "load_annotation",
        "load_misleep_anno",
        "signal_filter",
        "spectrogram",
        "spectrum",
        "band_power",
        "SWA_detection",
        "spindle_detection",
        "auto_stage_gbm",
        "plot_signals",
        "plot_hypno",
    ]:
        assert hasattr(misleep, name), f"missing public API: {name}"


@pytest.mark.skipif(not _pyside6_available(), reason="PySide6 not installed")
def test_gui_imports_and_window():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    from misleep.gui.main_window import MainWindow
    from misleep.gui.spec_window import SpecWindow

    window = MainWindow()
    spec = SpecWindow()
    assert spec is not None
    window.is_saved = True
    window.close()
    spec.close()


@pytest.mark.skipif(not _pyside6_available(), reason="PySide6 not installed")
def test_cli_arg_parsing():
    from misleep.gui.app import _parse_args

    # positional: data, then annotation
    data, anno = _parse_args(["rec.mat", "rec.txt"])
    assert data == "rec.mat"
    assert anno == "rec.txt"
    # flags
    data, anno = _parse_args(["--data", "a.edf", "--anno", "b.txt"])
    assert data == "a.edf" and anno == "b.txt"
    # data flag + positional annotation
    data, anno = _parse_args(["--data", "a.edf", "b.txt"])
    assert data == "a.edf" and anno == "b.txt"
    # nothing
    data, anno = _parse_args([])
    assert data is None and anno is None


@pytest.mark.skipif(not _pyside6_available(), reason="PySide6 not installed")
def test_gui_signal_boxes(tmp_path):
    """The signal panel uses one box (axes) per channel."""
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])

    import datetime

    import numpy as np

    from misleep.data import MiData
    from misleep.gui.main_window import MainWindow

    rng = np.random.default_rng(0)
    sf = 256.0
    data = MiData(
        signals=[rng.standard_normal(int(sf * 120)) * 50,
                 rng.standard_normal(int(sf * 120)) * 30],
        channels=["EEG", "EMG"],
        sf=[sf, sf],
        time="20240409-18:00:00",
    )
    window = MainWindow()
    window.midata = data
    window.ac_time = datetime.datetime.strptime(data.time, "%Y%m%d-%H:%M:%S")
    window.check_show()
    window.plot_signals()

    # spectrogram strip + one box per channel (2 channels -> 3 axes)
    assert len(window.signal_ax) == 3
    # every channel box has exactly one signal trace
    for i in range(2):
        traces = [l for l in window.signal_ax[i + 1].get_lines()
                  if l.get_linewidth() == 0.5]
        assert len(traces) == 1

    # markers / start-end lines drawn on every channel box
    window.mianno.marker.append([10.5, "injection"])
    window.start_end = [20, 40]
    window.plot_marker_line()
    window.plot_start_end_line()
    assert len(window.signal_marker_axvline) >= 2

    window.is_saved = True
    window.close()


@pytest.mark.skipif(not _pyside6_available(), reason="PySide6 not installed")
def test_gui_channel_reorder():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])

    import datetime

    import numpy as np

    from misleep.data import MiData
    from misleep.gui.main_window import MainWindow

    rng = np.random.default_rng(0)
    sf = 256.0
    data = MiData(
        signals=[rng.standard_normal(int(sf * 120)),
                 rng.standard_normal(int(sf * 120))],
        channels=["EEG", "EMG"],
        sf=[sf, sf],
        time="20240409-18:00:00",
    )
    window = MainWindow()
    window.midata = data
    window.ac_time = datetime.datetime.strptime(data.time, "%Y%m%d-%H:%M:%S")
    window.check_show()

    new_order = ["EMG", "EEG"]
    window.channel_slm.setChannels(new_order)  # what drag & drop produces
    window.channel_moved(None, 0, 1, None, 0)
    assert window.midata.channels == new_order
    assert window.show_idx == [0, 1]
    assert list(window.horizontal_line.keys()) == new_order
    window.plot_signals()

    window.is_saved = True
    window.close()


@pytest.mark.skipif(not _pyside6_available(), reason="PySide6 not installed")
def test_gui_channel_rename_duplicate():
    """Renaming a channel to an existing name adds a suffix and must not
    desynchronize the horizontal_line registry (regression test)."""
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])

    import datetime

    import numpy as np

    from misleep.data import MiData
    from misleep.gui.main_window import MainWindow

    rng = np.random.default_rng(0)
    sf = 256.0
    data = MiData(
        signals=[rng.standard_normal(int(sf * 60)),
                 rng.standard_normal(int(sf * 60))],
        channels=["EEG_P", "EMG_DIFF"],
        sf=[sf, sf],
        time="20240409-18:00:00",
    )
    window = MainWindow()
    window.midata = data
    window.ac_time = datetime.datetime.strptime(data.time, "%Y%m%d-%H:%M:%S")
    window.check_show()

    # rename EEG_P -> EMG_DIFF (duplicate -> becomes EMG_DIFF_1)
    window.channel_slm.setChannels(["EMG_DIFF", "EMG_DIFF"])
    window.channel_rename()
    assert window.midata.channels == ["EMG_DIFF_1", "EMG_DIFF"]
    assert set(window.horizontal_line.keys()) == set(window.midata.channels)
    window.plot_signals()  # must not raise KeyError

    window.is_saved = True
    window.close()


@pytest.mark.skipif(not _pyside6_available(), reason="PySide6 not installed")
def test_gui_spectrum_window(tmp_path, monkeypatch):
    """Opening the spectrum window must not raise (regression)."""
    from PySide6.QtWidgets import QApplication, QMessageBox

    app = QApplication.instance() or QApplication([])

    boxes = []
    monkeypatch.setattr(QMessageBox, "about", staticmethod(
        lambda *a, **k: boxes.append(a[1:])))

    from misleep.gui.main_window import MainWindow

    window = MainWindow()
    window.open_data(str(__import__("pathlib").Path(__file__).parent / "data" / "10mins_example_mat.mat"))
    window.show()
    app.processEvents()

    sm = window.ChListView.selectionModel()
    sm.select(window.channel_slm.index(0), sm.SelectionFlag.ClearAndSelect)
    window.start_end = [10, 60]
    window.show_spec_window()

    assert not boxes, f"unexpected message boxes: {boxes}"
    assert window.spec_window.isVisible()

    window.is_saved = True
    window.close()


@pytest.mark.skipif(not _pyside6_available(), reason="PySide6 not installed")
def test_gui_move_channel_buttons():
    """The Up/Down buttons move the selected channel and keep names."""
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])

    import datetime

    import numpy as np

    from misleep.data import MiData
    from misleep.gui.main_window import MainWindow

    rng = np.random.default_rng(0)
    sf = 256.0
    data = MiData(
        signals=[rng.standard_normal(int(sf * 60)) for _ in range(3)],
        channels=["EEG", "EMG", "REF"],
        sf=[sf, sf, sf],
        time="20240409-18:00:00",
    )
    window = MainWindow()
    window.midata = data
    window.ac_time = datetime.datetime.strptime(data.time, "%Y%m%d-%H:%M:%S")
    window.fill_channel_listView()
    window.check_show()

    sm = window.ChListView.selectionModel()
    sm.select(window.channel_slm.index(1), sm.SelectionFlag.ClearAndSelect)  # EMG
    window.move_channel("up")
    assert window.midata.channels == ["EMG", "EEG", "REF"]
    window.move_channel("down")
    window.move_channel("down")
    assert window.midata.channels == ["EEG", "REF", "EMG"]

    # boundary moves are no-ops: up on the top item, down on the bottom
    sm.select(window.channel_slm.index(0), sm.SelectionFlag.ClearAndSelect)
    before = list(window.midata.channels)
    window.move_channel("up")
    assert window.midata.channels == before
    sm.select(window.channel_slm.index(2), sm.SelectionFlag.ClearAndSelect)
    before = list(window.midata.channels)
    window.move_channel("down")
    assert window.midata.channels == before

    # names are untouched
    assert sorted(window.midata.channels) == ["EEG", "EMG", "REF"]

    window.is_saved = True
    window.close()


@pytest.mark.skipif(not _pyside6_available(), reason="PySide6 not installed")
def test_gui_menu_meta_docks():
    """Menu bar visible; unified sidebar replaces the docks; wheel guard works."""
    from PySide6.QtCore import QPoint, QPointF, Qt
    from PySide6.QtGui import QWheelEvent
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])

    from misleep.gui.event_filters import WheelInputGuard
    from misleep.gui.main_window import MainWindow

    window = MainWindow()
    window.show()
    app.processEvents()
    # menu bar is back on top
    assert not window.menuBar.isHidden()
    # the unified sidebar replaces the four old docks
    assert window.sidebar_scroll.widget() is window.sidebar
    assert len(window._sections) == 4
    for dock in (window.MetaDock, window.ChannelDock,
                 window.AnnotationDock, window.TimeDock):
        assert dock.isHidden()
    # the app icon is applied
    assert not window.windowIcon().isNull()

    # wheel over a spin box is swallowed
    spin = window.FilterLowSpin
    before = spin.value()
    guard = WheelInputGuard(app)
    import PySide6.QtWidgets as qtw

    orig = qtw.QApplication.widgetAt
    qtw.QApplication.widgetAt = staticmethod(lambda pos: spin)
    ev = QWheelEvent(QPointF(0, 0), QPointF(0, 0), QPoint(0, -120), QPoint(0, -120),
                     Qt.MouseButton.NoButton, Qt.KeyboardModifier.NoModifier,
                     Qt.ScrollPhase.NoScrollPhase, False)
    try:
        assert guard.eventFilter(spin, ev) is True
    finally:
        qtw.QApplication.widgetAt = orig
    assert spin.value() == before

    window.is_saved = True
    window.close()


@pytest.mark.skipif(not _pyside6_available(), reason="PySide6 not installed")
def test_gui_wheel_page_flip():
    """Wheel over the signal/hypnogram panels flips pages."""
    from PySide6.QtCore import QPoint, QPointF, Qt
    from PySide6.QtGui import QWheelEvent
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])

    import datetime

    import numpy as np

    from misleep.data import MiData
    from misleep.gui.main_window import MainWindow

    rng = np.random.default_rng(0)
    sf = 256.0
    data = MiData(
        signals=[rng.standard_normal(int(sf * 300))],
        channels=["EEG"], sf=[sf], time="20240409-18:00:00")
    window = MainWindow()
    window.midata = data
    window.ac_time = datetime.datetime.strptime(data.time, "%Y%m%d-%H:%M:%S")
    window.fill_channel_listView()
    window.check_show()
    window.show()
    app.processEvents()

    sec0 = window.current_sec
    down = QWheelEvent(QPointF(0, 0), QPointF(0, 0), QPoint(0, -120), QPoint(0, -120),
                       Qt.MouseButton.NoButton, Qt.KeyboardModifier.NoModifier,
                       Qt.ScrollPhase.NoScrollPhase, False)
    app.sendEvent(window.SignalArea.viewport(), down)
    assert window.current_sec == sec0 + window.show_duration

    up = QWheelEvent(QPointF(0, 0), QPointF(0, 0), QPoint(0, 120), QPoint(0, 120),
                     Qt.MouseButton.NoButton, Qt.KeyboardModifier.NoModifier,
                     Qt.ScrollPhase.NoScrollPhase, False)
    app.sendEvent(window.hypo_canvas, up)
    assert window.current_sec < sec0 + window.show_duration

    window.is_saved = True
    window.close()


@pytest.mark.skipif(not _pyside6_available(), reason="PySide6 not installed")
def test_gui_event_list_dialog():
    """Marker / start-end list viewer: see, jump, delete."""
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])

    import datetime

    from misleep.gui.dialogs import EventListDialog
    from misleep.gui.main_window import MainWindow

    window = MainWindow()
    window.midata = __import__("misleep").MiData(
        signals=[__import__("numpy").zeros(256 * 100)],
        channels=["EEG"], sf=[256.0], time="20240409-18:00:00")
    window.ac_time = datetime.datetime.strptime("20240409-18:00:00", "%Y%m%d-%H:%M:%S")
    window.fill_channel_listView()
    window.check_show()
    window.mianno.marker.append([30.5, "injection"])
    window.mianno.start_end.append([50, 70, "spindle"])

    dialog = EventListDialog(window)
    dialog.show_events(kind="marker")
    assert dialog.list.count() == 1
    dialog.show_events(kind="start_end")
    assert dialog.list.count() == 1

    dialog._kind = "marker"
    dialog._refresh()
    dialog.list.setCurrentRow(0)
    dialog._jump()
    assert window.current_sec == 30

    dialog._kind = "marker"
    dialog._refresh()
    dialog.list.setCurrentRow(0)
    dialog._delete()
    assert len(window.mianno.marker) == 0

    window.is_saved = True
    window.close()


@pytest.mark.skipif(not _pyside6_available(), reason="PySide6 not installed")
def test_gui_horizontal_line_sd_multiplier():
    """Relative SD line must honor the entered multiplier (regression)."""
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])

    import datetime

    import numpy as np

    from misleep.data import MiData
    from misleep.gui.dialogs import HorizontalLineDialog
    from misleep.gui.main_window import MainWindow

    rng = np.random.default_rng(0)
    sf = 256.0
    data = MiData(
        signals=[rng.standard_normal(int(sf * 60)) * 100],
        channels=["EEG"], sf=[sf], time="20240409-18:00:00")

    window = MainWindow()
    window.midata = data
    window.ac_time = datetime.datetime.strptime(data.time, "%Y%m%d-%H:%M:%S")
    window.fill_channel_listView()
    window.horizontal_line = {"EEG": []}

    dialog = HorizontalLineDialog()
    dialog.midata = data
    dialog.horizontal_line = window.horizontal_line
    dialog.current_channel = "EEG"
    dialog.UseRelativeCheckBox.setChecked(True)
    dialog.RelativeCalComboBox.setCurrentIndex(0)  # Standard deviation

    sd = np.std(data.signals[0])
    dialog.RelativeNumEditor.setValue(3.0)
    dialog.add_line()
    assert abs(window.horizontal_line["EEG"][-1][0] - 3 * sd) < 1e-6

    dialog.RelativeNumEditor.setValue(0.5)
    dialog.add_line()
    assert abs(window.horizontal_line["EEG"][-1][0] - 0.5 * sd) < 1e-6

    window.is_saved = True
    window.close()


@pytest.mark.skipif(not _pyside6_available(), reason="PySide6 not installed")
def test_gui_state_buttons_and_shortcuts(monkeypatch, tmp_path):
    """4 default states; up to 10 states; keys 0-9 label by state code."""
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QKeyEvent
    from PySide6.QtWidgets import QApplication, QMessageBox

    # isolate the user config into a temp dir (the test saves 10 states)
    from misleep import config as config_module

    monkeypatch.setattr(config_module, "get_data_dir", lambda: tmp_path)
    monkeypatch.setattr("misleep.logger.get_data_dir", lambda: tmp_path)

    app = QApplication.instance() or QApplication([])
    QMessageBox.information = staticmethod(lambda *a, **k: None)

    import json

    from misleep.config import load_config
    from misleep.gui.config_dialog import SettingsDialog
    from misleep.gui.main_window import MainWindow

    # default config has exactly 4 states
    assert list(json.loads(load_config()["gui"]["statemap"]).keys()) == ["1", "2", "3", "4"]

    window = MainWindow()
    window.open_data(str(__import__("pathlib").Path(__file__).parent / "data" / "10mins_example_mat.mat"))
    window.show()
    app.processEvents()

    # 4 colored state buttons in the annotation dock
    assert len(window._state_btns) == 4
    assert window._state_btns[1].text() == "1:NREM"

    # key 3 labels state 3
    window.start_end = [5, 15]
    ev3 = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_3,
                    Qt.KeyboardModifier.NoModifier, "3")
    window.keyPressEvent(ev3)
    assert window.mianno.sleep_state[10] == 3

    # add states up to 10 via the settings dialog; key 0 then labels state 10
    dialog = SettingsDialog(window)
    for _ in range(6):
        dialog._add_state()
    assert len(dialog._state_rows) == 10
    dialog._ok()
    app.processEvents()
    assert len(window._state_btns) == 10 and 10 in window._state_btns
    # Settings -> Apply/OK must rebuild the hypnogram immediately, before
    # any new label is drawn.
    tick_labels = [label.get_text() for label in window.hypo_ax.get_yticklabels()]
    assert "State 10" in tick_labels

    window.start_end = [20, 30]
    ev0 = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_0,
                    Qt.KeyboardModifier.NoModifier, "0")
    window.keyPressEvent(ev0)
    assert window.mianno.sleep_state[25] == 10

    window.is_saved = True
    window.close()


@pytest.mark.skipif(not _pyside6_available(), reason="PySide6 not installed")
def test_compact_control_geometry():
    """Main-window and dialog controls stay compact under the app theme."""
    from PySide6.QtWidgets import QApplication, QPushButton

    app = QApplication.instance() or QApplication([])
    from misleep.gui.config_dialog import SettingsDialog
    from misleep.gui.main_window import MainWindow

    window = MainWindow()
    dialog = SettingsDialog(window)
    window.show()
    dialog.show()
    app.processEvents()

    assert window.SaveLabelBt.height() <= 32
    assert window.FilterLowSpin.height() <= 32
    assert dialog.findChildren(QPushButton)[0].height() <= 32
    assert window.SleepStateRadio.text() == "State"
    assert window.LabelBt.isHidden()
    state_widths = [button.width() for button in window._state_btns.values()]
    assert max(state_widths) - min(state_widths) <= 2
    assert window.sidebar.width() <= window.sidebar_scroll.viewport().width()
    assert window.ShowRangeCombo.width() >= window.gridLayout_4.geometry().width() - 20

    # Every primary-button pseudo-state must target every button.  A selector
    # such as ``#A, #B:disabled`` would leave A permanently styled disabled.
    from misleep.gui.style import build_stylesheet

    stylesheet = build_stylesheet("light")
    assert "#FilterConfirmBt:disabled" in stylesheet
    assert "#MultipleScalerConfirmBt:disabled" in stylesheet

    dialog.close()
    window.is_saved = True
    window.close()


@pytest.mark.skipif(not _pyside6_available(), reason="PySide6 not installed")
def test_interface_color_tone_presets_are_distinct():
    from misleep.gui.style import COLOR_TONES, resolved_theme

    assert set(COLOR_TONES) == {"black", "pink", "blue", "khaki"}
    accents = {name: resolved_theme("light", name)["accent"]
               for name in COLOR_TONES}
    assert len(set(accents.values())) == 4
    assert resolved_theme("light", "black")["text"] == "#151515"


@pytest.mark.skipif(not _pyside6_available(), reason="PySide6 not installed")
def test_settings_dialog_live_apply(monkeypatch, tmp_path):
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])

    # isolate the user config into a temp dir
    from misleep import config as config_module

    monkeypatch.setattr(config_module, "get_data_dir", lambda: tmp_path)
    monkeypatch.setattr("misleep.logger.get_data_dir", lambda: tmp_path)

    from misleep.gui.config_dialog import SettingsDialog
    from misleep.gui.main_window import MainWindow

    window = MainWindow()
    dialog = SettingsDialog(window)

    # change state 1 color, state 2 name and the first marker label
    dialog._state_rows[1][1].set_color("#123456")
    dialog._state_rows[2][0].setText("REMS")
    dialog._marker_editor.list.item(0).setText("new_marker")
    dialog._ok()

    assert window.state_color_dict[1] == "#123456"
    assert window.state_map_dict[2] == "REMS"
    assert window.label_dialog.marker_label[0] == "new_marker"
    assert window.config["gui"]["statecolor"].startswith('{"1": "#123456"')

    # applied settings persist to the (temp) user config
    assert (tmp_path / "misleep_config.ini").exists()

    window.is_saved = True
    window.close()


@pytest.mark.skipif(not _pyside6_available(), reason="PySide6 not installed")
def test_settings_dialog_collect(fresh_config):
    """The settings dialog collects valid config values."""
    import json

    from PySide6.QtWidgets import QApplication, QWidget

    app = QApplication.instance() or QApplication([])

    from misleep.config import load_config
    from misleep.gui.config_dialog import SettingsDialog

    class FakeMain(QWidget):
        config = load_config()

        def apply_settings(self):
            pass

    dialog = SettingsDialog(FakeMain())
    collected = dialog._collect()
    gui = collected["gui"]
    # JSON values must parse and keep int codes (colors normalize to hex)
    assert json.loads(gui["statemap"])["1"] == "NREM"
    assert json.loads(gui["statecolor"])["1"] == "#ffa500"
    assert json.loads(gui["statecolor"])["4"] == "#ececec"
    assert "marker" in gui and "startend" in gui
    assert float(gui["statecolorbgalpha"]) == 0.1
    assert float(gui["hypnogramstatealpha"]) == 0.55
    assert gui["color_tone"] == "black"
    assert json.loads(gui["freq_range"]) == [0.5, 30.0]
    assert float(collected["spec"]["gaussian_sigma"]) == 1.0


@pytest.mark.skipif(not _pyside6_available(), reason="PySide6 not installed")
def test_gui_with_data(tmp_path):
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])

    import datetime

    import numpy as np

    from misleep.data import MiData
    from misleep.gui.main_window import MainWindow

    rng = np.random.default_rng(0)
    sf = 256.0
    data = MiData(
        signals=[rng.standard_normal(int(sf * 120)) * 50],
        channels=["EEG"],
        sf=[sf],
        time="20240409-18:00:00",
    )
    window = MainWindow()
    window.midata = data
    window.ac_time = datetime.datetime.strptime(data.time, "%Y%m%d-%H:%M:%S")
    window.check_show()
    window.plot_signals()
    window.plot_hypo()
    assert window.total_seconds == 120
    window.is_saved = True
    window.close()
