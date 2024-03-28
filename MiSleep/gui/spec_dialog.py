# -*- coding: UTF-8 -*-
"""
@Project: MiSleep_v2 
@File: spec_window.py
@Author: Xueqiang Wang
@Date: 2024/3/8
@Description:  
"""

from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QDialog

from misleep.gui.uis.spec_window_ui import Ui_SpecDialog


class spec_dialog(QDialog, Ui_SpecDialog):
    def __init__(self, parent=None):
        """
        Initialize the spectrum dialog of MiSleep
        """
        super().__init__(parent)

        # Enable high dpi devices
        QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        self.setupUi(self)

    def closeEvent(self, event):
        event.ignore()
        self.hide()

