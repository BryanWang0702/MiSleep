# -*- coding: UTF-8 -*-
"""art_detection
@Project: MiSleep_v2 
@File: label_dialog.py
@Author: Xueqiang Wang
@Date: 2024/3/28
@Description:  Dialog file, label dialog, transfer result dialog
"""
from PyQt5.QtCore import QCoreApplication, Qt, QStringListModel
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QDialog, QMessageBox, QFileDialog, QColorDialog
import datetime
import numpy as np

from misleep.gui.uis.label_dialog_ui import Ui_Dialog
from misleep.gui.uis.transfer_result_dialog_ui import Ui_TransferResultDialog
from misleep.gui.uis.state_spectral_dialog_ui import Ui_StateSpectralDialog
from misleep.gui.uis.horizontal_line_dialog_ui import Ui_horizontal_line_dialog
from misleep.gui.thread import SaveThread
from misleep.io.annotation_io import transfer_result
from misleep.utils.signals import signal_filter
from misleep.utils.annotation import lst2group
from misleep.gui.utils import cal_draw_spectrum
from misleep.preprocessing.signals import reject_artifact
import pandas as pd
from copy import deepcopy


class label_dialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None, config=None):
        """
        Initialize the Label dialog of MiSleep
        """
        super().__init__(parent)

        # Enable high dpi devices
        QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        self.setupUi(self)

        # Load configuration
        self.config = config

        # Type representing marker(0) or start_end(1)
        self._type = 0

        # List view of selected labels
        self.slm = QStringListModel()
        self.LabelListView.setModel(self.slm)
        self.marker_label = [each[1:-1] for each in 
                             self.config['gui']['marker'][1:-1].split(', ')]
        self.start_end_label = [each[1:-1] for each in 
                                self.config['gui']['startend'][1:-1].split(', ')]
        self.label_name = ""
        self.closed = False

        self.OKBt.clicked.connect(self.submit_label)
        self.CancelBt.clicked.connect(self.cancel_event)
        self.AddBt.clicked.connect(self.add_label)
        self.DeleteBt.clicked.connect(self.delete_label)

        self.slm.dataChanged.connect(self.update_label_list)
        self.add_or_delete = False


    def show_contents(self, idx=0):
        """Show label contents"""
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

    def submit_label(self):
        """Triggered by Clicking Ok Button"""
        
        if self._type == 0:
            self.label_name = self.marker_label[
                self.LabelListView.selectedIndexes()[0].row()
            ]
        
        else:
            self.label_name = self.start_end_label[
                self.LabelListView.selectedIndexes()[0].row()
            ]

        self.hide()

    def update_label_list(self):
        """Update label list when edited"""
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
            self.marker_label.append('label')
        elif self._type == 1:
            self.start_end_label.append('start end label')
        
        self.add_or_delete = True
        self.update_label_list()

    def delete_label(self):
        if not self.LabelListView.selectedIndexes():
            return
        if len(self.slm.stringList()) == 1:
            QMessageBox.about(self, "Error", "You can't delete all labels!")
            return
        if self._type == 0:
            self.marker_label.pop(
                self.LabelListView.selectedIndexes()[0].row()
            )
        elif self._type == 1:
            self.start_end_label.pop(
                self.LabelListView.selectedIndexes()[0].row()
            )
        self.add_or_delete = True
        self.update_label_list()

    def save_config(self):
        """When label changed, save configuration to file, open a new thread"""
        self.config.set('gui', 'MARKER', str(self.marker_label))
        self.config.set('gui', 'STARTEND', str(self.start_end_label))
        save_thread = SaveThread(file=self.config, 
                                 file_path='./misleep/config.ini')
        save_thread.save_config()
        save_thread.quit()
    
    def cancel_event(self):
        """Triggered by the `cancel` button"""
        self.closed = True
        self.hide()
    
    def closeEvent(self, event):
        event.ignore()
        self.closed = True
        self.hide()


class transferResult_dialog(QDialog, Ui_TransferResultDialog):
    def __init__(self, parent=None):
        """
        Initialize the transfer dialog of MiSleep
        """
        super().__init__(parent)

        # Enable high dpi devices
        QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        self.setupUi(self)

        self.ACTimeEditor.setDisabled(True)
        self.TransferStartTimeEdit.setDisabled(True)
        self.ResetTimeCheckBox.clicked.connect(self.ac_time_editor_changed)
        self.ResetTransferStartTimeCheckBox.clicked.connect(self.start_time_editor_changed)
        self.OKBt.clicked.connect(self.okEvent)
        self.CancelBt.clicked.connect(self.cancelEvent)
        self.closed = True
        
    def ac_time_editor_changed(self):
        if self.ResetTimeCheckBox.isChecked():
            self.ACTimeEditor.setEnabled(True)
        if not self.ResetTimeCheckBox.isChecked():
            self.ACTimeEditor.setDisabled(True)

    def start_time_editor_changed(self):
        if self.ResetTransferStartTimeCheckBox.isChecked():
            self.TransferStartTimeEdit.setEnabled(True)
        if not self.ResetTransferStartTimeCheckBox.isChecked():
            self.TransferStartTimeEdit.setDisabled(True)

    def transfer(self, config, mianno, ac_time):
        """Transfer result to dataframe, triggered by okay button"""
        mianno = deepcopy(mianno)
        ac_time = deepcopy(ac_time)

        if self.ResetTimeCheckBox.isChecked():
            ac_time = self.ACTimeEditor.dateTime().toPyDateTime()
        else:
            ac_time = datetime.datetime.strptime(ac_time, "%Y%m%d-%H:%M:%S")
        
        if self.ResetTransferStartTimeCheckBox.isChecked():
            start_time = self.TransferStartTimeEdit.dateTime().toPyDateTime()
            if start_time > ac_time:
                delay_seconds = (start_time - ac_time).seconds
                mianno._marker = mianno.marker[delay_seconds:]
                mianno._start_end = mianno.start_end[delay_seconds:]
                mianno._sleep_state = mianno.sleep_state[delay_seconds:]
                ac_time = start_time

        df, analyse_df, start_end_df, marker_df = transfer_result(mianno=mianno, ac_time=ac_time)        
        
        fd, _ = QFileDialog.getSaveFileName(self, "Save transfered result",
                                                f"{config['gui']['openpath'].split('/')[0]}/transfer_result.xlsx", 
                                                "*.xlsx;;")
        if fd == '':
            return

        try:
            writer = pd.ExcelWriter(fd, datetime_format='yyyy-mm-dd hh:mm:ss')
            pd.concat([df, analyse_df], axis=1).to_excel(
                excel_writer=writer, sheet_name='Sleep state', index=False)
            
            start_end_df.to_excel(excel_writer=writer, sheet_name='Start End', index=False)

            marker_df.to_excel(excel_writer=writer, sheet_name='Marker', index=False)
            
            writer.close()
        except PermissionError as e:
            QMessageBox.about(self, "Error", "Close the EXCEL sheet first.")
            return

        QMessageBox.about(self, "Info", "Transfered result saved")

    def okEvent(self):
        self.closed = False
        self.hide()

    def cancelEvent(self):
        """Triggered by the `cancel` button"""
        self.closed = True
        self.hide()
    
    def closeEvent(self, event):
        event.ignore()
        self.closed = True
        self.hide()


class stateSpectral_dialog(QDialog, Ui_StateSpectralDialog):
    def __init__(self, parent=None):
        """
        Initialize the state spectral dialog of MiSleep
        """
        super().__init__(parent)

        # Enable high dpi devices
        QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        self.setupUi(self)

        self.BPFilterCheckBox.clicked.connect(self.BP_filter_check_changed)
        self.BPFilterCheckBox.setChecked(True)
        self.RejectArtifactCheckBox.setChecked(False)
        self.ArtThresholdSpinBox.setDisabled(True)
        self.RejectArtifactCheckBox.clicked.connect(self.reject_artifact_artifacts_changed)
        self.StartTimeEditor.setDisabled(True)
        self.EndTimeEditor.setDisabled(True)
        self.StartTimeCheckBox.clicked.connect(self.start_time_editor_changed)
        self.EndTimeCheckBox.clicked.connect(self.end_time_editor_changed)
        
        self.OKBt.clicked.connect(self.okEvent)
        self.CancelBt.clicked.connect(self.cancelEvent)
        self.closed = True

    def start_time_editor_changed(self):
        if self.StartTimeCheckBox.isChecked():
            self.StartTimeEditor.setEnabled(True)
        if not self.StartTimeCheckBox.isChecked():
            self.StartTimeEditor.setDisabled(True)

    def end_time_editor_changed(self):
        if self.EndTimeCheckBox.isChecked():
            self.EndTimeEditor.setEnabled(True)
        if not self.EndTimeCheckBox.isChecked():
            self.EndTimeEditor.setDisabled(True)

    def BP_filter_check_changed(self):
        if self.BPFilterCheckBox.isChecked():
            self.BPLow.setEnabled(True)
            self.BPHigh.setEnabled(True)
        if not self.BPFilterCheckBox.isChecked():
            self.BPLow.setDisabled(True)
            self.BPHigh.setDisabled(True)

    def reject_artifact_artifacts_changed(self):
        if self.RejectArtifactCheckBox.isChecked():
            self.ArtThresholdSpinBox.setEnabled(True)
        if not self.RejectArtifactCheckBox.isChecked():
            self.ArtThresholdSpinBox.setDisabled(True)

    def dialog_show(self, channels):
        """Show state spectral dialog, fill params"""
        self.ChannelSelector.clear()
        self.ChannelSelector.addItems(channels)
        self.ChannelSelector.setCurrentIndex(0)

    def spectral_analysis(self, midata, mianno, config):
        """Do spectral analysis"""

        mianno = deepcopy(mianno)
        midata = deepcopy(midata)

        ac_time = datetime.datetime.strptime(midata.time, "%Y%m%d-%H:%M:%S")
        start_sec = 0
        end_sec = mianno.anno_length
        
        if self.StartTimeCheckBox.isChecked():
            start_time = self.StartTimeEditor.dateTime().toPyDateTime()
            start_sec = int(datetime.timedelta.total_seconds(start_time - ac_time))
        
        if self.EndTimeCheckBox.isChecked():
            end_time = self.EndTimeEditor.dateTime().toPyDateTime()
            end_sec = int(datetime.timedelta.total_seconds(end_time - ac_time))

        if end_sec <= start_sec:
            start_sec = 0
            end_sec = mianno.anno_length
            
        midata = midata.crop([start_sec, end_sec])
        sleep_state = mianno.sleep_state[start_sec:end_sec+1]

        # if list(set(sleep_state)) == [4]:
        #     QMessageBox.about(self, "Warning", "No state for spectral analysis")

        channel_idx = self.ChannelSelector.currentIndex()
        channel_data = midata.signals[channel_idx]
        sleep_state = lst2group([[idx, each] for idx, each in enumerate(sleep_state)])
        sf = midata.sf[channel_idx]

        # Do filter if checked
        if self.BPFilterCheckBox.isChecked():
            low = self.BPLow.value()
            high = self.BPHigh.value()
            channel_data, _ = signal_filter(channel_data, sf=sf, btype='bandpass',
                                         low=low, high=high)
            
        # Merge 4 states' data
        NREM_data = [channel_data[int(each[0]*sf): int(each[1]*sf)] 
                     for each in sleep_state if each[2] == 1]
        NREM_data = [element for sublist in NREM_data for element in sublist]
        REM_data = [channel_data[int(each[0]*sf): int(each[1]*sf)] 
                     for each in sleep_state if each[2] == 2]
        REM_data = [element for sublist in REM_data for element in sublist]
        Wake_data = [channel_data[int(each[0]*sf): int(each[1]*sf)] 
                     for each in sleep_state if each[2] == 3]
        Wake_data = [element for sublist in Wake_data for element in sublist]
        Init_data = [channel_data[int(each[0]*sf): int(each[1]*sf)] 
                     for each in sleep_state if each[2] == 4]
        Init_data = [element for sublist in Init_data for element in sublist]

        # Reject artifact if checked
        if self.RejectArtifactCheckBox.isChecked():
            threshold = self.ArtThresholdSpinBox.value()
        else:
            threshold = 1.5
        if self.RejectArtifactCheckBox.isChecked():
            NREM_data = reject_artifact(NREM_data, sf=sf, threshold=threshold)
            REM_data = reject_artifact(REM_data, sf=sf, threshold=threshold)
            Wake_data = reject_artifact(Wake_data, sf=sf, threshold=threshold)
            Init_data = reject_artifact(Init_data, sf=sf, threshold=threshold)

        nperseg = 10*sf
        if self.RelativeCheckBox.isChecked():
            relative = True
        else:
            relative = False
        NREM_spec, NREM_figure = cal_draw_spectrum(data=NREM_data, sf=sf, 
                                                   nperseg=nperseg, relative=relative)
        REM_spec, REM_figure = cal_draw_spectrum(data=REM_data, sf=sf, 
                                                   nperseg=nperseg, relative=relative)
        Wake_spec, Wake_figure = cal_draw_spectrum(data=Wake_data, sf=sf,
                                                   nperseg=nperseg, relative=relative)

        name_map = {
            1: 'NREM',
            2: 'REM',
            3: 'Wake',
            4: 'Init'
        }

        fd = QFileDialog.getExistingDirectory(self, 
                                              "Select a folder to save 4 stages' data", 
                                              f"{config['gui']['openpath']}")
        if fd == '':
            return

        # Save figure
        NREM_figure.savefig(fd+'/NREM_spectrum.pdf')
        REM_figure.savefig(fd+'/REM_spectrum.pdf')
        Wake_figure.savefig(fd+'/Wake_spectrum.pdf')
        writer = pd.ExcelWriter(fd+'/power_results.xlsx')

        # Write to excel file
        for idx, spec in enumerate([NREM_spec, REM_spec, Wake_spec]):
            _df = pd.DataFrame(data=spec.T, columns=['frequency', 'power'])
            _df.to_excel(excel_writer=writer, sheet_name=name_map[idx+1], index=False)
        if len(Init_data) > sf*10:
            Init_spec, Init_figure = cal_draw_spectrum(data=Init_data, sf=sf,
                                                   nperseg=nperseg, relative=relative)
            _df = pd.DataFrame(data=Init_spec.T, columns=['frequency', 'power'])
            _df.to_excel(excel_writer=writer, sheet_name=name_map[4], index=False)
            Init_figure.savefig(fd + '/Init_spectrum.pdf')

        writer.close()

        QMessageBox.about(self, "Info", "Spectral analysis finished")

    def okEvent(self):
        self.closed = False
        self.hide()

    def cancelEvent(self):
        """Triggered by the `cancel` button"""
        self.closed = True
        self.hide()
    
    def closeEvent(self, event):
        event.ignore()
        self.closed = True
        self.hide()


class horizontalLine_dialog(QDialog, Ui_horizontal_line_dialog):
    def __init__(self, parent=None):
        """
        Initialize the horizontal line dialog of MiSleep
        """
        super().__init__(parent)

        # Enable high dpi devices
        QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        self.setupUi(self)

        self.color = '#ff0000'

        # initial color button
        self.SetColorBt.setText(self.color)
        self.SetColorBt.setStyleSheet(f"background-color:{'red'}")
        self.SetColorBt.clicked.connect(self.select_color)

        self.AddLineBt.clicked.connect(self.add_line)
        self.DeleteLineBt.clicked.connect(self.delete_line)

        self.OKBt.clicked.connect(self.okEvent)
        self.CancelBt.clicked.connect(self.cancelEvent)

        self.relative_methods_dict = {0: 'Standard deviation', 1: 'Mean'}

        # channel list view model
        self.line_slm = QStringListModel()

        # Current selected channel
        self.current_channel = None

        # the horizontal line dict
        self.horizontal_line = None

        self.UseRelativeCheckBox.clicked.connect(self.click_relative_checkbox)
        self.RelativeCalComboBox.setDisabled(True)
        self.RelativeNumEditor.setEnabled(False)

        self.ChannelComboBox.currentIndexChanged.connect(self.chCombo_change)

        self.closed = True
        self.appled = False

        self.midata = None  # For SD or Mean calculation

    def click_relative_checkbox(self):
        """Unlock relative combox and num editor"""
        if self.UseRelativeCheckBox.isChecked():
            self.RelativeCalComboBox.setDisabled(False)
            self.RelativeNumEditor.setEnabled(True)
            self.SelfDefineValueEditor.setDisabled(True)
        else:
            self.RelativeCalComboBox.setDisabled(True)
            self.RelativeNumEditor.setEnabled(False)
            self.SelfDefineValueEditor.setDisabled(False)

    def show_chs(self):
        """Initial channel combox"""
        self.ChannelComboBox.clear()
        self.ChannelComboBox.addItems(list(self.horizontal_line.keys()))
        self.ChannelComboBox.setCurrentIndex(0)
        self.current_channel = list(self.horizontal_line.keys())[0]
        self.show_lines()

    def chCombo_change(self):
        """Channel combox change, reset the channel show list"""
        current_channel_idx = self.ChannelComboBox.currentIndex()
        self.current_channel = list(self.horizontal_line.keys())[current_channel_idx]
        self.show_lines()

    def show_lines(self):
        """Show lines in the listview"""
        strs = [f'{each[0]}_{each[1]}_{each[2]}' for each in self.horizontal_line[self.current_channel]]
        self.line_slm.setStringList(strs)
        self.LineListView.setModel(self.line_slm)

    def add_line(self):
        """Add a horizontan line, triggered by AddLineBt"""
        if self.UseRelativeCheckBox.isChecked():
            method_idx = self.RelativeCalComboBox.currentIndex()
            if method_idx == 0:
                # Standard deviation
                value = np.std(self.midata.signals[self.midata.channels.index(self.current_channel)])
                comment = 'SD'
            elif method_idx == 1:
                value = np.mean(self.midata.signals[self.midata.channels.index(self.current_channel)])
                comment = 'Mean'
            else:
                value = 0
                comment ='self defined'
        else:
            value = self.SelfDefineValueEditor.value()
            comment = 'self defined'
        
        self.horizontal_line[self.current_channel].append([value, self.color, comment])

        self.show_lines()

    def delete_line(self):
        """Delete line with selected index"""
        selected_line = [each.row() for each in self.LineListView.selectedIndexes()]
        if len(selected_line) == 0:
            return
        self.horizontal_line[self.current_channel].pop(selected_line[0])
        self.show_lines()

    def select_color(self):
        c = QColorDialog.getColor(initial=QColor(255, 0, 0))
        self.color = c.name()
        if self.color == '#000000':
            self.color = '#ff0000'
        self.SetColorBt.setText(self.color)
        self.SetColorBt.setStyleSheet(f"background-color:{self.color}")

    def okEvent(self):
        self.closed = False
        self.hide()

    def cancelEvent(self):
        """Triggered by the `cancel` button"""
        self.closed = True
        self.hide()
    
    def closeEvent(self, event):
        event.ignore()
        self.closed = True
        self.hide()
