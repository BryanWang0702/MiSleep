# -*- coding: UTF-8 -*-
"""
@Project: MiSleep_v2 
@File: show.py
@Author: Xueqiang Wang
@Date: 2024/3/8
@Description:  
"""
import sys
import os
sys.path.append(os.getcwd())
print(os.getcwd())
from PyQt5.QtWidgets import QApplication


def show():
    from misleep.gui.main_window import main_window
    app = QApplication(sys.argv)
    main_win = main_window()
    main_win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    show()
