# -*- coding: UTF-8 -*-
"""art_detection
@Project: MiSleep_v2 
@File: label_dialog.py
@Author: Xueqiang Wang
@Date: 2024/3/28
@Description:  Dialog file, label dialog, transfer result dialog
"""
from PyQt5.QtCore import QCoreApplication, Qt, QStringListModel
from PyQt5.QtWidgets import QDialog, QMessageBox, QFileDialog
import datetime

from misleep.gui.uis.label_dialog_ui import Ui_Dialog
from misleep.gui.uis.transfer_result_dialog_ui import Ui_TransferResultDialog
from misleep.gui.uis.state_spectral_dialog_ui import Ui_StateSpectralDialog
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
        
        
        fd, _ = QFileDialog.getSaveFileName(self, "Save transfered result",
                                                f"{config['gui']['openpath'].split('/')[0]}/transfer_result.xlsx", 
                                                "*.xlsx;;")
        if fd == '':
            return
        
        df, analyse_df, start_end_df, marker_df = transfer_result(mianno=mianno, ac_time=ac_time)

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
        
        self.OKBt.clicked.connect(self.okEvent)
        self.CancelBt.clicked.connect(self.cancelEvent)
        self.closed = True

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

        channel_idx = self.ChannelSelector.currentIndex()
        channel_data = midata.signals[channel_idx]
        sleep_state = lst2group([[idx, each] for idx, each in enumerate(mianno.sleep_state)])
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

        








