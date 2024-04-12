# -*- coding: UTF-8 -*-
"""
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
from misleep.gui.thread import SaveThread
from misleep.gui.utils import transfer_time, insert_row, temp_loop4below_row
from misleep.utils.annotation import lst2group
import pandas as pd


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
        self.ResetTimeCheckBox.clicked.connect(self.enable_time_editor)
        
    def enable_time_editor(self):
        self.ACTimeEditor.setEnabled(True)

    def transfer(self, config, mianno, ac_time):
        """Transfer result to dataframe, triggered by okay button"""

        if self.ResetTimeCheckBox.isChecked():
            ac_time = self.ACTimeEditor.dateTime().toPyDateTime()
        else:
            ac_time = datetime.datetime.strptime(ac_time, "%Y%m%d-%H:%M:%S")
        marker = [[
            transfer_time(ac_time, each[0], '%Y-%m-%d %H:%M:%S'), 
            each[0], each[1]] for each in mianno.marker]

        start_end_label = [[
            transfer_time(ac_time, each[0], '%Y-%m-%d %H:%M:%S', ms=True), each[0], 1,
            transfer_time(ac_time, each[1], '%Y-%m-%d %H:%M:%S', ms=True), each[1], 0,
            each[2]
        ] for each in mianno.start_end]

        sleep_state = lst2group([[idx+1, each] 
                                 for idx, each in enumerate(mianno.sleep_state)])
        sleep_state = [[
            transfer_time(ac_time, each[0], '%Y-%m-%d %H:%M:%S'), each[0], 1,
            transfer_time(ac_time, each[1], '%Y-%m-%d %H:%M:%S'), each[1], 0,
            each[2], mianno.state_map[each[2]]
        ] for each in sleep_state]

        columns=['start_time', 'start_time_sec', 'start_code',
                 'end_time', 'end_time_sec', 'end_code',
                 'state_code', 'state']

        df = pd.DataFrame(data=sleep_state, columns=columns)
        
        new_df = pd.DataFrame(columns=columns)
        for idx, row in df.iterrows():
            if row['end_time_sec'] % 3600 == 0:
                new_df = insert_row(new_df, idx, row)
                # Just add a row and nothing else
                new_row = pd.Series([
                    row['end_time'], row['end_time_sec'], ' ',
                    row['end_time'], row['end_time_sec'], '5',
                    ' ', 'MARKER'
                ], index=columns)
                new_df = insert_row(new_df, new_df.shape[0], new_row)
                continue

            if int(row['end_time_sec'] / 3600) > int(row['start_time_sec'] / 3600):

                previous_row, new_row, below_row = temp_loop4below_row(row, ac_time, columns)

                new_df = insert_row(new_df, new_df.shape[0], previous_row)
                new_df = insert_row(new_df, new_df.shape[0], new_row)
                while int(below_row['end_time_sec'] / 3600) > int(below_row['start_time_sec'] / 3600):
                    row = below_row
                    previous_row, new_row, below_row = temp_loop4below_row(row, ac_time, columns)
                    new_df = insert_row(new_df, new_df.shape[0], previous_row)
                    new_df = insert_row(new_df, new_df.shape[0], new_row)

                new_df = insert_row(new_df, new_df.shape[0], below_row)
                continue

            new_df = insert_row(new_df, new_df.shape[0], row)

        df = new_df
        del new_df

        df['bout_duration'] = df.apply(
            lambda x: x[4] - x[1] + 1 if x[7] != 'MARKER' else '', axis=1)
        
        df['hour'] = df['start_time_sec'].apply(lambda x: int(x / 3600) if x % 3600 != 0 else '')
        analyse_df = pd.DataFrame()

        temp_hour = list(set(list(df['hour'])))
        temp_hour.remove('')
        temp_hour = sorted(temp_hour)
        analyse_df['date_time'] = [transfer_time(ac_time, each*3600, "%Y-%m-%d %M:%H:%S")
                                for each in temp_hour]

        features = []
        for each in temp_hour:
            df_ = df[df['hour'] == each]
            temp_lst = []
            for phase in ["NREM", "REM", "Wake", "INIT"]:
                _duration = df_[df_["state"] == phase]["bout_duration"].sum()
                _bout = df_[df_["state"] == phase]["bout_duration"].count()
                temp_lst += [_duration, _bout, round(_duration / _bout, 2) if _bout != 0 else 0, round(_duration / 3600, 2)]
            features.append(temp_lst)

        analyse_df[['NREM_duration', 'NREM_bout', "NREM_ave", "NREM_percentage",
                    'REM_duration', 'REM_bout', "REM_ave", "REM_percentage",
                    'WAKE_duration', 'WAKE_bout', "WAKE_ave", "WAKE_percentage",
                    'INIT_duration', 'INIT_bout', "INIT_ave", "INIT_percentage"]] = features


        analyse_df[
            ['NREM_duration', 'NREM_bout', 'REM_duration', 'REM_bout', 'WAKE_duration',
            'WAKE_bout', 'INIT_duration', 'INIT_bout']
        ] = analyse_df[
            ['NREM_duration', 'NREM_bout', 'REM_duration', 'REM_bout', 'WAKE_duration',
            'WAKE_bout', 'INIT_duration', 'INIT_bout']].astype(int)
        
        fd, _ = QFileDialog.getSaveFileName(self, "Save transfered result",
                                                f"{config['gui']['openpath'].split('/')[0]}/transfer_result.xlsx", 
                                                "*.xlsx;;")
        if fd == '':
            return

        writer = pd.ExcelWriter(fd, datetime_format='yyyy-mm-dd hh:mm:ss')
        pd.concat([df, analyse_df], axis=1).to_excel(
            excel_writer=writer, sheet_name='All', index=False)
        
        writer.close()

        QMessageBox.about(self, "Info", "Transfered result saved")

    def cancel_event(self):
        """Triggered by the `cancel` button"""
        self.closed = True
        self.hide()
    
    def closeEvent(self, event):
        event.ignore()
        self.closed = True
        self.hide()

    


