# -*- coding: UTF-8 -*-
"""
@Project: MiSleep_v2 
@File: about.py
@Author: Xueqiang Wang
@Date: 2024/3/8
@Description:  
"""
from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtWidgets import QDialog

from misleep.gui.uis.about_ui import Ui_AboutDialog


class about_dialog(QDialog, Ui_AboutDialog):
    def __init__(self, parent=None, version=None, update_time=None):
        """
        Initialize the About dialog of MiSleep
        """
        super().__init__(parent)

        # Enable high dpi devices
        QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        self.setupUi(self)
        if version:
            self.VersionLabel.setText(f"Version: {version}")
        if update_time:
            self.UpdateLabel.setText(f"Update: {update_time}")


