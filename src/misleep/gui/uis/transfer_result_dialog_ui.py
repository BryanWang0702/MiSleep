# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'transfer_result_dialog.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QDateTimeEdit, QDialog,
    QGridLayout, QGroupBox, QPushButton, QSizePolicy,
    QSpacerItem, QWidget)
from misleep.gui.resources import misleep_rc

class Ui_TransferResultDialog(object):
    def setupUi(self, TransferResultDialog):
        if not TransferResultDialog.objectName():
            TransferResultDialog.setObjectName(u"TransferResultDialog")
        TransferResultDialog.resize(271, 216)
        icon = QIcon()
        icon.addFile(u":/logo/logo.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        TransferResultDialog.setWindowIcon(icon)
        self.gridLayout_2 = QGridLayout(TransferResultDialog)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.OKBt = QPushButton(TransferResultDialog)
        self.OKBt.setObjectName(u"OKBt")

        self.gridLayout_2.addWidget(self.OKBt, 1, 0, 1, 1)

        self.CancelBt = QPushButton(TransferResultDialog)
        self.CancelBt.setObjectName(u"CancelBt")

        self.gridLayout_2.addWidget(self.CancelBt, 1, 1, 1, 1)

        self.groupBox = QGroupBox(TransferResultDialog)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.TransferStartTimeEdit = QDateTimeEdit(self.groupBox)
        self.TransferStartTimeEdit.setObjectName(u"TransferStartTimeEdit")

        self.gridLayout.addWidget(self.TransferStartTimeEdit, 3, 0, 1, 1)

        self.ResetTimeCheckBox = QCheckBox(self.groupBox)
        self.ResetTimeCheckBox.setObjectName(u"ResetTimeCheckBox")

        self.gridLayout.addWidget(self.ResetTimeCheckBox, 0, 0, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 1, 1, 1, 1)

        self.ACTimeEditor = QDateTimeEdit(self.groupBox)
        self.ACTimeEditor.setObjectName(u"ACTimeEditor")

        self.gridLayout.addWidget(self.ACTimeEditor, 1, 0, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 3, 1, 1, 1)

        self.ResetTransferStartTimeCheckBox = QCheckBox(self.groupBox)
        self.ResetTransferStartTimeCheckBox.setObjectName(u"ResetTransferStartTimeCheckBox")

        self.gridLayout.addWidget(self.ResetTransferStartTimeCheckBox, 2, 0, 1, 1)


        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 2)


        self.retranslateUi(TransferResultDialog)

        QMetaObject.connectSlotsByName(TransferResultDialog)
    # setupUi

    def retranslateUi(self, TransferResultDialog):
        TransferResultDialog.setWindowTitle(QCoreApplication.translate("TransferResultDialog", u"Dialog", None))
        self.OKBt.setText(QCoreApplication.translate("TransferResultDialog", u"OK", None))
        self.CancelBt.setText(QCoreApplication.translate("TransferResultDialog", u"Cancel", None))
        self.groupBox.setTitle(QCoreApplication.translate("TransferResultDialog", u"Transfer result options", None))
        self.TransferStartTimeEdit.setDisplayFormat(QCoreApplication.translate("TransferResultDialog", u"yyyy/MM/dd HH:mm:ss", None))
        self.ResetTimeCheckBox.setText(QCoreApplication.translate("TransferResultDialog", u"Reset acquisition time", None))
        self.ACTimeEditor.setDisplayFormat(QCoreApplication.translate("TransferResultDialog", u"yyyy/MM/dd HH:mm:ss", None))
        self.ResetTransferStartTimeCheckBox.setText(QCoreApplication.translate("TransferResultDialog", u"Reset transfer start time", None))
    # retranslateUi

