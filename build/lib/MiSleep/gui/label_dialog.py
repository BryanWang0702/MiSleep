# -*- coding: UTF-8 -*-
"""
@Project: MiSleep_v2 
@File: label_dialog.py
@Author: Xueqiang Wang
@Date: 2024/3/28
@Description:  
"""
from PyQt5.QtCore import QCoreApplication, Qt, QStringListModel
from PyQt5.QtWidgets import QDialog, QMessageBox
import json

from misleep.gui.uis.label_dialog_ui import Ui_Dialog
from misleep.gui.thread import SaveThread


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

