# -*- coding: UTF-8 -*-
"""Dialog windows of the MiSleep GUI.

Contains the label picker, result transfer dialog, state spectral
analysis dialog, horizontal-line dialog, SWA/spindle detection dialogs,
the two auto-staging dialogs and the save-data dialog, plus the About box.
"""

import datetime
import os
from copy import deepcopy

import numpy as np
import pandas as pd
from PySide6.QtCore import Qt, QStringListModel
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from misleep.analysis.detection import SWA_detection, spindle_detection
from misleep.config import save_config
from misleep.gui.qt_utils import (
    app_icon,
    cal_draw_spectrum,
    downsample_by_most_frequent,
    get_base_path,
)
from misleep.gui.uis.about_ui import Ui_AboutDialog
from misleep.gui.uis.auto_stage_causalTransformer_dialog_ui import Ui_AutoStageCausalTransformerDialog
from misleep.gui.uis.auto_stage_lightGBM_dialog_ui import Ui_AutoStageLightGBMDialog
from misleep.gui.uis.horizontal_line_dialog_ui import Ui_horizontal_line_dialog
from misleep.gui.uis.label_dialog_ui import Ui_Dialog
from misleep.gui.uis.save_data_dialog_ui import Ui_SaveDataDialog
from misleep.gui.uis.spindle_detect_dialog_ui import Ui_SpindleDetectDialog
from misleep.gui.uis.state_spectral_dialog_ui import Ui_StateSpectralDialog
from misleep.gui.uis.SWA_detect_dialog_ui import Ui_SWADetectDialog
from misleep.gui.uis.transfer_result_dialog_ui import Ui_TransferResultDialog
from misleep.gui.workers import SaveThread
from misleep.io.annotation import transfer_result
from misleep.logger import logger
from misleep.preprocessing.artifacts import reject_artifact
from misleep.preprocessing.filtering import signal_filter
from misleep.utils.annotation import lst2group


class AboutDialog(QDialog, Ui_AboutDialog):
    """The About box of MiSleep."""

    def __init__(self, parent=None, version=None, update_time=None):
        super().__init__(parent)
        self.setupUi(self)
        if version:
            self.VersionLabel.setText(f"Version: {version}")
        if update_time:
            self.UpdateLabel.setText(f"Update: {update_time}")


class LabelDialog(QDialog, Ui_Dialog):
    """Pick a marker / start-end label from the configured lists."""

    def __init__(self, parent=None, config=None):
        super().__init__(parent)
        self.setupUi(self)

        self.config = config

        # Type representing marker(0) or start_end(1)
        self._type = 0

        self.slm = QStringListModel()
        self.LabelListView.setModel(self.slm)
        self.marker_label = [each[1:-1] for each in
                             self.config["gui"]["marker"][1:-1].split(", ")]
        self.start_end_label = [each[1:-1] for each in
                                self.config["gui"]["startend"][1:-1].split(", ")]
        self.label_name = ""
        self.closed = False

        self.OKBt.clicked.connect(self.submit_label)
        self.CancelBt.clicked.connect(self.cancel_event)
        self.AddBt.clicked.connect(self.add_label)
        self.DeleteBt.clicked.connect(self.delete_label)

        self.slm.dataChanged.connect(self.update_label_list)
        self.add_or_delete = False

    def show_contents(self, idx=0):
        """Show the label list for the current type."""
        self.closed = False

        if self._type == 0:
            self.slm.setStringList(self.marker_label)
            self.LabelListView.setModel(self.slm)
        if self._type == 1:
            self.slm.setStringList(self.start_end_label)
            self.LabelListView.setModel(self.slm)

        if idx == -1:
            idx = len(self.slm.stringList()) - 1
        idx = self.slm.index(idx)
        self.LabelListView.setCurrentIndex(idx)

    def keyPressEvent(self, event):
        """Number keys select a label directly."""
        if Qt.Key.Key_0 <= event.key() <= Qt.Key.Key_9:
            if int(event.text()) <= len(self.slm.stringList()):
                idx = self.slm.index(int(event.text()) - 1)
                self.LabelListView.setCurrentIndex(idx)
        else:
            QWidget.keyPressEvent(self, event)

    def submit_label(self):
        """Triggered by the OK button."""
        if self._type == 0:
            self.label_name = self.marker_label[
                self.LabelListView.selectedIndexes()[0].row()]
        else:
            self.label_name = self.start_end_label[
                self.LabelListView.selectedIndexes()[0].row()]
        self.hide()

    def update_label_list(self):
        """Update the label list when edited."""
        if not self.add_or_delete:
            string_list = self.slm.stringList()
            if self._type == 0:
                self.marker_label = string_list
            if self._type == 1:
                self.start_end_label = string_list
        else:
            self.show_contents(idx=-1)
            self.add_or_delete = False
        self.save_config()

    def add_label(self):
        if self._type == 0:
            self.marker_label.append("label")
        elif self._type == 1:
            self.start_end_label.append("start end label")
        self.add_or_delete = True
        self.update_label_list()

    def delete_label(self):
        if not self.LabelListView.selectedIndexes():
            return
        if len(self.slm.stringList()) == 1:
            QMessageBox.about(self, "Error", "You can't delete all labels!")
            return
        if self._type == 0:
            self.marker_label.pop(self.LabelListView.selectedIndexes()[0].row())
        elif self._type == 1:
            self.start_end_label.pop(self.LabelListView.selectedIndexes()[0].row())
        self.add_or_delete = True
        self.update_label_list()

    def save_config(self):
        """Persist the (possibly edited) label lists to the user config."""
        self.config.set("gui", "MARKER", str(self.marker_label))
        self.config.set("gui", "STARTEND", str(self.start_end_label))
        save_thread = SaveThread(file=self.config)
        save_thread.save_config()

    def cancel_event(self):
        """Triggered by the Cancel button."""
        self.closed = True
        self.hide()

    def closeEvent(self, event):
        event.ignore()
        self.closed = True
        self.hide()


class TransferResultDialog(QDialog, Ui_TransferResultDialog):
    """Dialog for exporting the annotation to Excel statistics."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.ACTimeEditor.setDisabled(True)
        self.TransferStartTimeEdit.setDisabled(True)
        self.ResetTimeCheckBox.clicked.connect(self.ac_time_editor_changed)
        self.ResetTransferStartTimeCheckBox.clicked.connect(self.start_time_editor_changed)
        self.OKBt.clicked.connect(self.ok_event)
        self.CancelBt.clicked.connect(self.cancel_event)
        self.closed = True

    def ac_time_editor_changed(self):
        self.ACTimeEditor.setEnabled(self.ResetTimeCheckBox.isChecked())

    def start_time_editor_changed(self):
        self.TransferStartTimeEdit.setEnabled(self.ResetTransferStartTimeCheckBox.isChecked())

    def transfer(self, config, mianno, ac_time):
        """Transfer the annotation into analysis dataframes and save to Excel."""
        mianno = deepcopy(mianno)
        ac_time = deepcopy(ac_time)

        if self.ResetTimeCheckBox.isChecked():
            ac_time = self.ACTimeEditor.dateTime().toPython()
        else:
            ac_time = datetime.datetime.strptime(ac_time, "%Y%m%d-%H:%M:%S")

        if self.ResetTransferStartTimeCheckBox.isChecked():
            start_time = self.TransferStartTimeEdit.dateTime().toPython()
            if start_time > ac_time:
                delay_seconds = (start_time - ac_time).seconds
                mianno._marker = mianno.marker[delay_seconds:]
                mianno._start_end = mianno.start_end[delay_seconds:]
                mianno._sleep_state = mianno.sleep_state[delay_seconds:]
                ac_time = start_time

        df, analyse_df, start_end_df, marker_df = transfer_result(mianno=mianno, ac_time=ac_time)

        fd, _ = QFileDialog.getSaveFileName(
            self, "Save transfered result",
            f"{get_base_path(config['gui']['openpath'])}", "*.xlsx;;")
        if fd == "":
            return

        try:
            writer = pd.ExcelWriter(fd, datetime_format="yyyy-mm-dd hh:mm:ss")
            pd.concat([df, analyse_df], axis=1).to_excel(
                excel_writer=writer, sheet_name="Sleep state", index=False)
            start_end_df.to_excel(excel_writer=writer, sheet_name="Start End", index=False)
            marker_df.to_excel(excel_writer=writer, sheet_name="Marker", index=False)
            writer.close()
        except PermissionError as e:
            logger.error(f"Permission error: {e}")
            QMessageBox.about(self, "Error", "Close the EXCEL sheet first.")
            return

        QMessageBox.about(self, "Info", "Transfered result saved")

    def ok_event(self):
        self.closed = False
        self.hide()

    def cancel_event(self):
        self.closed = True
        self.hide()

    def closeEvent(self, event):
        event.ignore()
        self.closed = True
        self.hide()


class StateSpectralDialog(QDialog, Ui_StateSpectralDialog):
    """Per-state spectral analysis dialog."""

    def __init__(self, parent=None, config=None):
        super().__init__(parent)
        self.setupUi(self)

        self.BPFilterCheckBox.clicked.connect(self.BP_filter_check_changed)
        self.BPFilterCheckBox.setChecked(True)
        self.RejectArtifactCheckBox.setChecked(False)
        self.ArtThresholdSpinBox.setDisabled(True)
        self.RejectArtifactCheckBox.clicked.connect(self.reject_artifact_changed)
        self.StartTimeEditor.setDisabled(True)
        self.EndTimeEditor.setDisabled(True)
        self.StartTimeCheckBox.clicked.connect(self.start_time_editor_changed)
        self.EndTimeCheckBox.clicked.connect(self.end_time_editor_changed)
        self.GaussianCheckBox.clicked.connect(self.gaussian_check_changed)
        self.GaussianCheckBox.setChecked(False)
        self.GaussianSpinBox.setDisabled(True)
        self.GaussianSpinBox.setValue(float(config["spec"]["gaussian_sigma"]))
        self.WinLengthCheckBox.clicked.connect(self.win_length_check_changed)
        self.WinLengthCheckBox.setChecked(False)
        self.WinLengthSpinBox.setDisabled(True)
        self.WinLengthSpinBox.setValue(float(config["spec"]["win_length_sec"]))
        self.nfftCheckBox.clicked.connect(self.nfft_check_changed)
        self.nfftCheckBox.setChecked(False)
        self.nfftSpinBox.setDisabled(True)
        self.nfftSpinBox.setValue(int(float(config["spec"]["nfft_sec"])))

        self.OKBt.clicked.connect(self.ok_event)
        self.CancelBt.clicked.connect(self.cancel_event)
        self.closed = True

    def start_time_editor_changed(self):
        self.StartTimeEditor.setEnabled(self.StartTimeCheckBox.isChecked())

    def end_time_editor_changed(self):
        self.EndTimeEditor.setEnabled(self.EndTimeCheckBox.isChecked())

    def BP_filter_check_changed(self):
        enabled = self.BPFilterCheckBox.isChecked()
        self.BPLow.setEnabled(enabled)
        self.BPHigh.setEnabled(enabled)

    def reject_artifact_changed(self):
        self.ArtThresholdSpinBox.setEnabled(self.RejectArtifactCheckBox.isChecked())

    def gaussian_check_changed(self):
        self.GaussianSpinBox.setEnabled(self.GaussianCheckBox.isChecked())

    def win_length_check_changed(self):
        self.WinLengthSpinBox.setEnabled(self.WinLengthCheckBox.isChecked())

    def nfft_check_changed(self):
        self.nfftSpinBox.setEnabled(self.nfftCheckBox.isChecked())

    def dialog_show(self, channels):
        """Fill the channel selector."""
        self.ChannelSelector.clear()
        self.ChannelSelector.addItems(channels)
        self.ChannelSelector.setCurrentIndex(0)

    def spectral_analysis(self, midata, mianno, config):
        """Run the state spectral analysis and export results."""
        mianno = deepcopy(mianno)
        midata = deepcopy(midata)

        ac_time = datetime.datetime.strptime(midata.time, "%Y%m%d-%H:%M:%S")
        start_sec = 0
        end_sec = mianno.anno_length

        if self.StartTimeCheckBox.isChecked():
            start_time = self.StartTimeEditor.dateTime().toPython()
            start_sec = int(datetime.timedelta.total_seconds(start_time - ac_time))
        if self.EndTimeCheckBox.isChecked():
            end_time = self.EndTimeEditor.dateTime().toPython()
            end_sec = int(datetime.timedelta.total_seconds(end_time - ac_time))

        if end_sec <= start_sec:
            start_sec = 0
            end_sec = mianno.anno_length

        midata = midata.crop([start_sec, end_sec])
        sleep_state = mianno.sleep_state[start_sec:end_sec + 1]

        channel_idx = self.ChannelSelector.currentIndex()
        channel_data = midata.signals[channel_idx]
        sleep_state = lst2group([[idx, each] for idx, each in enumerate(sleep_state)])
        sf = midata.sf[channel_idx]

        # Band-pass filter if checked
        freq_band = [self.BPLow.value(), self.BPHigh.value()]
        if self.BPFilterCheckBox.isChecked():
            channel_data, _ = signal_filter(channel_data, sf=sf, btype="bandpass",
                                            low=freq_band[0], high=freq_band[1])

        win_length = self.WinLengthSpinBox.value() if self.WinLengthCheckBox.isChecked() else 10.0
        nperseg = int(sf * win_length)

        nfft = int(self.nfftSpinBox.value() * sf) if self.nfftCheckBox.isChecked() else None
        if nfft is not None and nfft < nperseg:
            nfft = None

        gaussian_sigma = self.GaussianSpinBox.value() if self.GaussianCheckBox.isChecked() else None

        state_codes = sorted(set(mianno.sleep_state[start_sec:end_sec + 1]))
        state_data = {
            state: np.concatenate([
                channel_data[int(each[0] * sf): int(each[1] * sf)]
                for each in sleep_state if each[2] == state
            ])
            for state in state_codes
        }

        threshold = self.ArtThresholdSpinBox.value() if self.RejectArtifactCheckBox.isChecked() else 1.5
        if self.RejectArtifactCheckBox.isChecked():
            state_data = {
                state: reject_artifact(data, sf=sf, threshold=threshold)
                for state, data in state_data.items()
            }

        relative = self.RelativeCheckBox.isChecked()
        spectra = {
            state: cal_draw_spectrum(data=data, sf=sf, nperseg=nperseg,
                                     freq_band=freq_band, relative=relative,
                                     nfft=nfft, gaussian_sigma=gaussian_sigma)
            for state, data in state_data.items()
        }

        name_map = mianno.state_map

        # Optional per-hour spectral segmentation
        hour_spec = {state: [] for state in spectra}
        if self.HourSegmentCheckBox.isChecked():
            for sec in range(0, end_sec - start_sec, 3600):
                hour_states = mianno.sleep_state[start_sec + sec:start_sec + sec + 3600]
                hour_states = lst2group([[idx + sec, each]
                                         for idx, each in enumerate(hour_states)])
                for state in spectra:
                    data_parts = [channel_data[int(each[0] * sf): int(each[1] * sf)]
                                  for each in hour_states if each[2] == state]
                    data = np.concatenate(data_parts) if data_parts else np.array([])
                    if self.RejectArtifactCheckBox.isChecked() and len(data):
                        data = reject_artifact(data, sf=sf, threshold=threshold)
                    if len(data) > sf * 10:
                        hour_spec[state].append(cal_draw_spectrum(
                            data=data, sf=sf, nperseg=nperseg,
                            freq_band=freq_band, relative=relative, nfft=nfft,
                            gaussian_sigma=gaussian_sigma)[0][1])

        fd = QFileDialog.getExistingDirectory(self, "Select a folder to save states' data",
                                              f"{config['gui']['openpath']}")
        if fd == "":
            return

        try:
            writer = pd.ExcelWriter(
                fd + f"/{os.path.basename(config['gui']['openpath']).split('.')[0]}_power_results.xlsx")

            for state, (spec, figure) in spectra.items():
                state_name = str(name_map.get(state, state))
                safe_name = "".join(c if c not in '\\/:*?"<>|' else "_" for c in state_name)
                figure.savefig(fd + "/" + safe_name + "_spectrum.pdf")
                _df = pd.DataFrame(data=spec.T, columns=["frequency", "power"])
                if hour_spec[state]:
                    _df[[str(each) for each in range(1, len(hour_spec[state]) + 1)]] = \
                        pd.DataFrame(hour_spec[state]).T
                _df.to_excel(excel_writer=writer, sheet_name=safe_name[:31], index=False)

            writer.close()
        except PermissionError as e:
            logger.error(f"Permission error: {e}")
            QMessageBox.about(self, "Error", "Close the PDF or EXCEL file under this folder first.")
            return
        QMessageBox.about(self, "Info", "Spectral analysis finished")

    def ok_event(self):
        self.closed = False
        self.hide()

    def cancel_event(self):
        self.closed = True
        self.hide()

    def closeEvent(self, event):
        event.ignore()
        self.closed = True
        self.hide()


class HorizontalLineDialog(QDialog, Ui_horizontal_line_dialog):
    """Dialog for adding horizontal reference lines to the signal plot."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.color = "#ff0000"
        self.SetColorBt.setText(self.color)
        self._style_color_bt()
        self.SetColorBt.clicked.connect(self.select_color)

        self.AddLineBt.clicked.connect(self.add_line)
        self.DeleteLineBt.clicked.connect(self.delete_line)
        self.OKBt.clicked.connect(self.ok_event)
        self.CancelBt.clicked.connect(self.cancel_event)

        self.relative_methods_dict = {0: "Standard deviation", 1: "Mean"}
        # the .ui ships with empty combo items; fill them here
        self.RelativeCalComboBox.clear()
        self.RelativeCalComboBox.addItems(list(self.relative_methods_dict.values()))
        self.RelativeNumEditor.setToolTip(
            "Line position = this number x SD (or x Mean) of the channel")

        self.line_slm = QStringListModel()
        self.current_channel = None
        self.horizontal_line = None

        self.UseRelativeCheckBox.clicked.connect(self.click_relative_checkbox)
        self.RelativeCalComboBox.setDisabled(True)
        self.RelativeNumEditor.setEnabled(False)
        self.ChannelComboBox.currentIndexChanged.connect(self.ch_combo_change)

        self.closed = True
        self.midata = None  # For SD/Mean calculation

    def click_relative_checkbox(self):
        checked = self.UseRelativeCheckBox.isChecked()
        self.RelativeCalComboBox.setDisabled(not checked)
        self.RelativeNumEditor.setEnabled(checked)
        self.SelfDefineValueEditor.setDisabled(checked)

    def show_chs(self):
        """Initialize the channel combobox."""
        self.ChannelComboBox.clear()
        self.ChannelComboBox.addItems(list(self.horizontal_line.keys()))
        self.ChannelComboBox.setCurrentIndex(0)
        self.current_channel = list(self.horizontal_line.keys())[0]
        self.show_lines()

    def ch_combo_change(self):
        current_channel_idx = self.ChannelComboBox.currentIndex()
        self.current_channel = list(self.horizontal_line.keys())[current_channel_idx]
        self.show_lines()

    def show_lines(self):
        strs = [f"{each[0]}_{each[1]}_{each[2]}"
                for each in self.horizontal_line[self.current_channel]]
        self.line_slm.setStringList(strs)
        self.LineListView.setModel(self.line_slm)

    def add_line(self):
        if self.UseRelativeCheckBox.isChecked():
            method_idx = self.RelativeCalComboBox.currentIndex()
            multiplier = self.RelativeNumEditor.value()
            if method_idx == 0:
                value = multiplier * np.std(self.midata.signals[self.midata.channels.index(self.current_channel)])
                comment = f"{multiplier:g} x SD"
            elif method_idx == 1:
                value = multiplier * np.mean(self.midata.signals[self.midata.channels.index(self.current_channel)])
                comment = f"{multiplier:g} x Mean"
            else:
                value = 0
                comment = "self defined"
        else:
            value = self.SelfDefineValueEditor.value()
            comment = "self defined"

        self.horizontal_line[self.current_channel].append([value, self.color, comment])
        self.show_lines()

    def delete_line(self):
        selected_line = [each.row() for each in self.LineListView.selectedIndexes()]
        if len(selected_line) == 0:
            return
        self.horizontal_line[self.current_channel].pop(selected_line[0])
        self.show_lines()

    def select_color(self):
        c = QColorDialog.getColor(initial=QColor(255, 0, 0))
        self.color = c.name()
        if self.color == "#000000":
            self.color = "#ff0000"
        self.SetColorBt.setText(self.color)
        self._style_color_bt()

    def _style_color_bt(self):
        """Style the swatch with readable text on any theme/color."""
        c = QColor(self.color)
        lum = 0.299 * c.red() + 0.587 * c.green() + 0.114 * c.blue()
        fg = "#000000" if lum > 150 else "#ffffff"
        self.SetColorBt.setStyleSheet(
            f"QPushButton {{ background-color: {self.color}; color: {fg};"
            f" border: 1px solid {self.color}; border-radius: 6px;"
            f" font-weight: 600; padding: 2px 8px; min-height: 24px; }}")

    def ok_event(self):
        self.closed = False
        self.hide()

    def cancel_event(self):
        self.closed = True
        self.hide()

    def closeEvent(self, event):
        event.ignore()
        self.closed = True
        self.hide()


class SWADetectionDialog(QDialog, Ui_SWADetectDialog):
    """Slow-wave activity detection dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.unit_map = {0: 1, 1: 1000, 2: 1000000}
        self.OKBt.clicked.connect(self.ok_event)
        self.CancelBt.clicked.connect(self.cancel_event)

    def show_chs(self, channels):
        self.ChannelComBox.clear()
        self.ChannelComBox.addItems(channels)
        self.ChannelComBox.setCurrentIndex(0)

    def swa_detection(self, midata, mianno, config):
        """Run SWA detection on the selected channel and states."""
        freq_low = self.FreqLowEditor.value()
        freq_high = self.FreqHighEditor.value()
        channel_idx = self.ChannelComBox.currentIndex()
        channel = midata.channels[channel_idx]
        signal_data = deepcopy(midata.pick_chs([channel]))
        signal_sf = signal_data.sf[0]
        signal_data = signal_data.signals[0]

        std_thresh = self.StdEditor.value()

        sleep_state = lst2group([[idx, each] for idx, each in enumerate(deepcopy(mianno.sleep_state))])
        swa_lst = []
        for state, state_name in [(1, "NREM"), (2, "REM"), (3, "Wake"), (4, "Init")]:
            checkbox = {1: self.NREMCheckbox, 2: self.REMCheckbox,
                        3: self.WakeCheckbox, 4: self.InitCheckbox}[state]
            if not checkbox.isChecked():
                continue
            amp_threshold_low, amp_threshold_high = self.get_state_thres(
                data=signal_data, sf=signal_sf, sleep_state=sleep_state,
                state=state, thres=std_thresh)
            for each in sleep_state:
                if each[2] == state and each[1] - each[0] > 5:
                    data_ = signal_data[int(each[0] * signal_sf): int(each[1] * signal_sf)]
                    swa_lst_ = SWA_detection(
                        data_, signal_sf, freq_band=[freq_low, freq_high],
                        amp_threshold=(amp_threshold_low, amp_threshold_high),
                        start_time_sec=each[0])
                    if swa_lst_ is None:
                        continue
                    for each in swa_lst_:
                        each.append(state_name)
                        swa_lst.append(each)

        if self.ExportCheckbox.isChecked():
            df = pd.DataFrame(swa_lst, columns=["StartTime", "NegTime", "MiddleTime",
                                                "PosTime", "EndTime", "Duration", "NegPeak",
                                                "PosPeak", "PTP", "Slope", "Frequency", "State"])
            fd, _ = QFileDialog.getSaveFileName(self, "Save SWA detection result",
                                                f"{config['gui']['openpath']}SWA_result.csv", "*.csv;;")
            if fd == "":
                return
            try:
                df.to_csv(fd, index=False)
            except PermissionError as e:
                logger.error(f"Permission error: {e}")
                QMessageBox.critical(self, "Error", f"Permission denied: {e}, close the file first")
                return

        logger.info(f"SWA_detection: Freq_thres: {[freq_low, freq_high]}, std_thresh: {std_thresh}")
        return swa_lst

    def get_state_thres(self, data, sf, sleep_state, state, thres):
        """Compute amplitude thresholds from the full state data."""
        all_data = [data[int(each[0] * sf): int(each[1] * sf)]
                    for each in sleep_state if each[2] == state]
        all_data = [item for each in all_data for item in each]
        mean_ = np.mean(all_data)
        std_ = np.std(all_data)
        return thres * std_ + mean_, 10 * std_ + mean_

    def ok_event(self):
        self.closed = False
        self.hide()

    def cancel_event(self):
        self.closed = True
        self.hide()

    def closeEvent(self, event):
        event.ignore()
        self.closed = True
        self.hide()


class SpindleDetectionDialog(QDialog, Ui_SpindleDetectDialog):
    """Sleep spindle detection dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.OKBt.clicked.connect(self.ok_event)
        self.CancelBt.clicked.connect(self.cancel_event)

    def show_chs(self, channels):
        self.ChannelComBox.clear()
        self.ChannelComBox.addItems(channels)
        self.ChannelComBox.setCurrentIndex(0)

    def spindle_detection(self, midata, mianno, config):
        """Run spindle detection on the selected channel and states."""
        freq_low = self.FreqLowEditor.value()
        freq_high = self.FreqHighEditor.value()
        channel_idx = self.ChannelComBox.currentIndex()
        channel = midata.channels[channel_idx]
        signal_data = deepcopy(midata.pick_chs([channel]))
        signal_sf = signal_data.sf[0]
        signal_data = signal_data.signals[0]

        std_thres_input = self.StdEditor.value()
        duration_thres_input = self.durationThresholdEditor.value()

        sleep_state = lst2group([[idx, each] for idx, each in enumerate(deepcopy(mianno.sleep_state))])
        spindle_lst = []
        for state, state_name in [(1, "NREM"), (2, "REM"), (3, "Wake"), (4, "Init")]:
            checkbox = {1: self.NREMCheckbox, 2: self.REMCheckbox,
                        3: self.WakeCheckbox, 4: self.InitCheckbox}[state]
            if not checkbox.isChecked():
                continue
            std_thres, duration_thres = self.get_state_thres(
                data=signal_data, sf=signal_sf, sleep_state=sleep_state, state=state,
                thres1=std_thres_input, thres2=duration_thres_input)
            for each in sleep_state:
                if each[2] == state and each[1] - each[0] > 5:
                    data_ = signal_data[int(each[0] * signal_sf): int(each[1] * signal_sf)]
                    spindle_lst_ = spindle_detection(
                        data_, signal_sf, freq_band=[freq_low, freq_high],
                        std_thresh=std_thres, duration_thresh=duration_thres,
                        start_time_sec=each[0])
                    if spindle_lst_ is None:
                        continue
                    for each in spindle_lst_:
                        each.append(state_name)
                        spindle_lst.append(each)

        if self.ExportCheckbox.isChecked():
            df = pd.DataFrame(spindle_lst, columns=["StartTime", "EndTime", "State"])
            fd, _ = QFileDialog.getSaveFileName(self, "Save spindle detection result",
                                                f"{config['gui']['openpath']}spindle_result.csv", "*.csv;;")
            if fd == "":
                return
            try:
                df.to_csv(fd, index=False)
            except PermissionError as e:
                logger.error(f"Permission denied: {e}")
                QMessageBox.critical(self, "Error", f"Permission denied: {e}, close the file first")
                return

        logger.info(f"Spindle_detection: Freq_thres: {[freq_low, freq_high]}, "
                    f"std_thresh_input: {std_thres_input}, "
                    f"duration_thresh_input: {duration_thres_input}")
        return spindle_lst

    def get_state_thres(self, data, sf, sleep_state, state, thres1, thres2):
        """Compute thresholds from the full state data."""
        all_data = [data[int(each[0] * sf): int(each[1] * sf)]
                    for each in sleep_state if each[2] == state]
        all_data = [item for each in all_data for item in each]
        mean_ = np.mean(all_data)
        std_ = np.std(all_data)
        return thres1 * std_ + mean_, thres2 * std_ + mean_

    def ok_event(self):
        self.closed = False
        self.hide()

    def cancel_event(self):
        self.closed = True
        self.hide()

    def closeEvent(self, event):
        event.ignore()
        self.closed = True
        self.hide()


class AutoStageLightGBMDialog(QDialog, Ui_AutoStageLightGBMDialog):
    """LightGBM auto-staging dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.OKBt.clicked.connect(self.ok_event)
        self.CancelBt.clicked.connect(self.cancel_event)

    def show_chs(self, channels):
        self.EEGChannelCombox.clear()
        self.EEGChannelCombox.addItems(channels)
        self.EEGChannelCombox.setCurrentIndex(0)
        self.EMGchannelCombox.clear()
        self.EMGchannelCombox.addItems(channels)
        self.EMGchannelCombox.setCurrentIndex(1)

    def auto_stage(self, midata, mianno):
        """Run LightGBM auto staging on the selected channels."""
        from misleep.analysis.auto_stage import auto_stage_gbm

        EEG_channel_idx = self.EEGChannelCombox.currentIndex()
        EMG_channel_idx = self.EMGchannelCombox.currentIndex()
        EEG = deepcopy(midata.signals[EEG_channel_idx])
        EMG = deepcopy(midata.signals[EMG_channel_idx])
        label = deepcopy(mianno._sleep_state)
        sf = deepcopy(midata.sf[EEG_channel_idx])

        EEG_site = ["P", "F"][self.EEGSiteCombox.currentIndex()]
        mouse_age = ["adult", "ado", "P30"][self.AgeCombox.currentIndex()]

        pred_label = auto_stage_gbm(EEG=EEG, EMG=EMG, label=label, sf=sf,
                                    EEG_channel=EEG_site, mouse_age=mouse_age)
        save_anno = self.SaveAnnoCheckbox.isChecked()
        return pred_label, save_anno

    def ok_event(self):
        self.closed = False
        self.hide()

    def cancel_event(self):
        self.closed = True
        self.hide()

    def closeEvent(self, event):
        event.ignore()
        self.closed = True
        self.hide()


class AutoStageCausalTransformerDialog(QDialog, Ui_AutoStageCausalTransformerDialog):
    """Causal-transformer auto-staging dialog (requires PyTorch)."""

    #: Whether the transformer backend is importable.
    available = True

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.OKBt.clicked.connect(self.ok_event)
        self.CancelBt.clicked.connect(self.cancel_event)

    def show_chs(self, channels):
        self.EEGChannelCombox.clear()
        self.EEGChannelCombox.addItems(channels)
        self.EEGChannelCombox.setCurrentIndex(0)
        self.EMGchannelCombox.clear()
        self.EMGchannelCombox.addItems(channels)
        self.EMGchannelCombox.setCurrentIndex(1)

    def auto_stage(self, midata, mianno):
        """Run transformer auto staging on the selected channels."""
        try:
            from misleep.analysis.transformer import AutoStageConfig, auto_stage_llm
        except ImportError as e:
            self.available = False
            raise ImportError(
                "The transformer auto-staging requires PyTorch. "
                "Install it with: pip install 'misleep[transformer]'") from e

        EEG_channel_idx = self.EEGChannelCombox.currentIndex()
        EMG_channel_idx = self.EMGchannelCombox.currentIndex()
        EEG = deepcopy(midata.signals[EEG_channel_idx])
        EMG = deepcopy(midata.signals[EMG_channel_idx])
        label = deepcopy(mianno._sleep_state)
        sf = deepcopy(midata.sf[EEG_channel_idx])

        config = AutoStageConfig()
        config.sf = sf
        config.label_stride_seconds = 5
        config.output_stride_seconds = 5
        label = downsample_by_most_frequent(label, 5)
        pred_label = auto_stage_llm(EEG=EEG, EMG=EMG, label=label, config=config)
        pred_label = [[each] * 5 for each in pred_label]
        pred_label = [item for each in pred_label for item in each]
        for idx in range(1, len(pred_label) - 1):
            label_ = pred_label[idx]
            if label_ == 4:
                pred_label[idx] = 3
            if label_ == 3 and pred_label[idx + 1] == 2:  # REM after Wake
                pred_label[idx + 1] = 1
            if pred_label[idx - 1] == pred_label[idx + 1] and pred_label[idx] != 3:
                pred_label[idx] = pred_label[idx - 1]
        save_anno = self.SaveAnnoCheckbox.isChecked()
        return pred_label, save_anno

    def ok_event(self):
        self.closed = False
        self.hide()

    def cancel_event(self):
        self.closed = True
        self.hide()

    def closeEvent(self, event):
        event.ignore()
        self.closed = True
        self.hide()


class SaveDataDialog(QDialog, Ui_SaveDataDialog):
    """Dialog for exporting (cropped) data."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.CropStartTimeEditor.setDisabled(True)
        self.CropEndTimeEditor.setDisabled(True)
        self.CropDataStartCheckBox.clicked.connect(self.crop_start_time_editor_changed)
        self.CropDataEndCheckBox.clicked.connect(self.crop_end_time_editor_changed)

        self.channel_slm = QStringListModel()
        self.OKBtn.clicked.connect(self.ok_event)
        self.CancelBtn.clicked.connect(self.cancel_event)
        self.closed = True

    def crop_start_time_editor_changed(self):
        self.CropStartTimeEditor.setEnabled(self.CropDataStartCheckBox.isChecked())

    def crop_end_time_editor_changed(self):
        self.CropEndTimeEditor.setEnabled(self.CropDataEndCheckBox.isChecked())

    def fill_midata_params(self, midata):
        """Fill channel list and crop time range from a MiData."""
        self.channel_slm.setStringList(midata.channels)
        self.ChannelListView.setModel(self.channel_slm)

        self.CropStartTimeEditor.setDateTime(
            datetime.datetime.strptime(midata.time, "%Y%m%d-%H:%M:%S"))
        end_time = datetime.datetime.strptime(midata.time, "%Y%m%d-%H:%M:%S") + \
            datetime.timedelta(seconds=midata.duration)
        self.CropEndTimeEditor.setDateTime(end_time)

    def ok_event(self):
        self.closed = False
        self.hide()

    def cancel_event(self):
        self.closed = True
        self.hide()

    def closeEvent(self, event):
        event.ignore()
        self.closed = True
        self.hide()


class EventListDialog(QDialog):
    """List the already-labeled marker / start-end events.

    Lets the user see every labeled event at a glance, jump to one with a
    double-click, and add or delete events.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Annotation events")
        self.resize(400, 440)
        self.setWindowIcon(app_icon())
        self._kind = "marker"

        layout = QVBoxLayout(self)
        self.hint = QLabel()
        self.hint.setWordWrap(True)
        layout.addWidget(self.hint)

        self.list = QListWidget()
        layout.addWidget(self.list, 1)
        self.list.itemDoubleClicked.connect(self._jump)

        btn_row = QHBoxLayout()
        jump_bt = QPushButton("Jump to")
        add_bt = QPushButton("Add")
        del_bt = QPushButton("Delete")
        close_bt = QPushButton("Close")
        jump_bt.clicked.connect(self._jump)
        add_bt.clicked.connect(self._add)
        del_bt.clicked.connect(self._delete)
        close_bt.clicked.connect(self.accept)
        for b in (jump_bt, add_bt, del_bt, close_bt):
            btn_row.addWidget(b)
        layout.addLayout(btn_row)

    # ------------------------------------------------------------------
    def _main(self):
        return self.parent()

    def show_events(self, kind="marker"):
        """Fill the list from the parent's annotation (kind: marker/start_end)."""
        self._kind = kind
        self.setWindowTitle("Markers" if kind == "marker" else "Start-End events")
        self._refresh()

    def _refresh(self):
        mianno = self._main().mianno
        self.list.clear()
        if self._kind == "marker":
            for each in mianno.marker:
                self.list.addItem(f"{each[0]:.3f} s — {each[1]}")
            self.hint.setText(
                f"{len(mianno.marker)} marker(s) — double-click to jump")
        else:
            for each in mianno.start_end:
                self.list.addItem(f"{each[0]:.3f} — {each[1]:.3f} s — {each[2]}")
            self.hint.setText(
                f"{len(mianno.start_end)} start-end event(s) — double-click to jump")

    def _jump(self):
        row = self.list.currentRow()
        if row < 0:
            return
        mianno = self._main().mianno
        if self._kind == "marker":
            t = mianno.marker[row][0]
        else:
            t = mianno.start_end[row][0]
        self._main().redraw_all(second=int(t))
        self.accept()

    def _add(self):
        main = self._main()
        mianno = main.mianno
        if self._kind == "marker":
            labels = main.label_dialog.marker_label
            label, ok = QInputDialog.getItem(self, "Add marker", "Label:",
                                             labels, 0, True)
            if ok and label:
                mianno.marker.append([float(main.current_sec), label])
        else:
            labels = main.label_dialog.start_end_label
            label, ok = QInputDialog.getItem(self, "Add start-end", "Label:",
                                             labels, 0, True)
            if ok and label:
                start = float(main.current_sec)
                mianno.start_end.append([start, start + 5, label])
        self._refresh()
        self._after_change()

    def _delete(self):
        row = self.list.currentRow()
        if row < 0:
            return
        mianno = self._main().mianno
        if self._kind == "marker":
            mianno.marker.pop(row)
        else:
            mianno.start_end.pop(row)
        self._refresh()
        self._after_change()

    def _after_change(self):
        main = self._main()
        main.is_saved = False
        main.AnnotationPathLabel.setText("*Annotation path:")
        main.plot_signals()
        main.plot_hypo()
