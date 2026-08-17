# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'label_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QDialog, QGridLayout,
    QListView, QPushButton, QSizePolicy, QWidget)
from misleep.gui.resources import misleep_rc

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(316, 442)
        icon = QIcon()
        icon.addFile(u":/logo/logo.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        Dialog.setWindowIcon(icon)
        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.CancelBt = QPushButton(Dialog)
        self.CancelBt.setObjectName(u"CancelBt")
        self.CancelBt.setAutoDefault(False)

        self.gridLayout.addWidget(self.CancelBt, 3, 1, 1, 1)

        self.OKBt = QPushButton(Dialog)
        self.OKBt.setObjectName(u"OKBt")

        self.gridLayout.addWidget(self.OKBt, 3, 0, 1, 1)

        self.AddBt = QPushButton(Dialog)
        self.AddBt.setObjectName(u"AddBt")

        self.gridLayout.addWidget(self.AddBt, 1, 0, 1, 1)

        self.LabelListView = QListView(Dialog)
        self.LabelListView.setObjectName(u"LabelListView")
        self.LabelListView.setEditTriggers(QAbstractItemView.DoubleClicked)

        self.gridLayout.addWidget(self.LabelListView, 0, 0, 1, 2)

        self.DeleteBt = QPushButton(Dialog)
        self.DeleteBt.setObjectName(u"DeleteBt")

        self.gridLayout.addWidget(self.DeleteBt, 1, 1, 1, 1)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.CancelBt.setText(QCoreApplication.translate("Dialog", u"Cancel", None))
        self.OKBt.setText(QCoreApplication.translate("Dialog", u"OK", None))
        self.AddBt.setText(QCoreApplication.translate("Dialog", u"+", None))
        self.DeleteBt.setText(QCoreApplication.translate("Dialog", u"-", None))
    # retranslateUi

