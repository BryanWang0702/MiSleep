# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'save_data_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QApplication, QCheckBox,
    QDateTimeEdit, QDialog, QGridLayout, QGroupBox,
    QLabel, QListView, QPushButton, QSizePolicy,
    QWidget)

class Ui_SaveDataDialog(object):
    def setupUi(self, SaveDataDialog):
        if not SaveDataDialog.objectName():
            SaveDataDialog.setObjectName(u"SaveDataDialog")
        SaveDataDialog.resize(409, 516)
        self.gridLayout_2 = QGridLayout(SaveDataDialog)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.OKBtn = QPushButton(SaveDataDialog)
        self.OKBtn.setObjectName(u"OKBtn")

        self.gridLayout_2.addWidget(self.OKBtn, 1, 0, 1, 1)

        self.CancelBtn = QPushButton(SaveDataDialog)
        self.CancelBtn.setObjectName(u"CancelBtn")

        self.gridLayout_2.addWidget(self.CancelBtn, 1, 1, 1, 1)

        self.ACTimeEdit = QGroupBox(SaveDataDialog)
        self.ACTimeEdit.setObjectName(u"ACTimeEdit")
        self.gridLayout = QGridLayout(self.ACTimeEdit)
        self.gridLayout.setObjectName(u"gridLayout")
        self.CropDataStartCheckBox = QCheckBox(self.ACTimeEdit)
        self.CropDataStartCheckBox.setObjectName(u"CropDataStartCheckBox")

        self.gridLayout.addWidget(self.CropDataStartCheckBox, 2, 0, 1, 1)

        self.CropStartTimeEditor = QDateTimeEdit(self.ACTimeEdit)
        self.CropStartTimeEditor.setObjectName(u"CropStartTimeEditor")

        self.gridLayout.addWidget(self.CropStartTimeEditor, 3, 0, 1, 1)

        self.ChannelListView = QListView(self.ACTimeEdit)
        self.ChannelListView.setObjectName(u"ChannelListView")
        self.ChannelListView.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        self.ChannelListView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ChannelListView.setTabKeyNavigation(True)
        self.ChannelListView.setSelectionMode(QAbstractItemView.MultiSelection)

        self.gridLayout.addWidget(self.ChannelListView, 1, 0, 1, 2)

        self.label_3 = QLabel(self.ACTimeEdit)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)

        self.CropDataEndCheckBox = QCheckBox(self.ACTimeEdit)
        self.CropDataEndCheckBox.setObjectName(u"CropDataEndCheckBox")

        self.gridLayout.addWidget(self.CropDataEndCheckBox, 4, 0, 1, 1)

        self.CropEndTimeEditor = QDateTimeEdit(self.ACTimeEdit)
        self.CropEndTimeEditor.setObjectName(u"CropEndTimeEditor")

        self.gridLayout.addWidget(self.CropEndTimeEditor, 5, 0, 1, 1)


        self.gridLayout_2.addWidget(self.ACTimeEdit, 0, 0, 1, 2)


        self.retranslateUi(SaveDataDialog)

        QMetaObject.connectSlotsByName(SaveDataDialog)
    # setupUi

    def retranslateUi(self, SaveDataDialog):
        SaveDataDialog.setWindowTitle(QCoreApplication.translate("SaveDataDialog", u"Dialog", None))
        self.OKBtn.setText(QCoreApplication.translate("SaveDataDialog", u"OK", None))
        self.CancelBtn.setText(QCoreApplication.translate("SaveDataDialog", u"Cancel", None))
        self.ACTimeEdit.setTitle(QCoreApplication.translate("SaveDataDialog", u"Save data options", None))
        self.CropDataStartCheckBox.setText(QCoreApplication.translate("SaveDataDialog", u"Crop data - Set Start Time", None))
        self.CropStartTimeEditor.setDisplayFormat(QCoreApplication.translate("SaveDataDialog", u"yyyy/MM/dd HH:mm:ss", None))
        self.label_3.setText(QCoreApplication.translate("SaveDataDialog", u"Select Channels to Save", None))
        self.CropDataEndCheckBox.setText(QCoreApplication.translate("SaveDataDialog", u"Crop data - Set End Time", None))
        self.CropEndTimeEditor.setDisplayFormat(QCoreApplication.translate("SaveDataDialog", u"yyyy/MM/dd HH:mm:ss", None))
    # retranslateUi

