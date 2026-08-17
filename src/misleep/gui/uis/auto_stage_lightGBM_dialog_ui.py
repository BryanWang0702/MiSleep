# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'auto_stage_lightGBM_dialog.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
    QGridLayout, QGroupBox, QLabel, QPushButton,
    QSizePolicy, QWidget)
from misleep.gui.resources import misleep_rc

class Ui_AutoStageLightGBMDialog(object):
    def setupUi(self, AutoStageLightGBMDialog):
        if not AutoStageLightGBMDialog.objectName():
            AutoStageLightGBMDialog.setObjectName(u"AutoStageLightGBMDialog")
        AutoStageLightGBMDialog.resize(408, 342)
        icon = QIcon()
        icon.addFile(u":/logo/logo.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        AutoStageLightGBMDialog.setWindowIcon(icon)
        self.gridLayout = QGridLayout(AutoStageLightGBMDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.OKBt = QPushButton(AutoStageLightGBMDialog)
        self.OKBt.setObjectName(u"OKBt")

        self.gridLayout.addWidget(self.OKBt, 1, 0, 1, 1)

        self.CancelBt = QPushButton(AutoStageLightGBMDialog)
        self.CancelBt.setObjectName(u"CancelBt")

        self.gridLayout.addWidget(self.CancelBt, 1, 1, 1, 1)

        self.groupBox = QGroupBox(AutoStageLightGBMDialog)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_2 = QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.AgeCombox = QComboBox(self.groupBox)
        self.AgeCombox.addItem("")
        self.AgeCombox.addItem("")
        self.AgeCombox.addItem("")
        self.AgeCombox.setObjectName(u"AgeCombox")

        self.gridLayout_2.addWidget(self.AgeCombox, 3, 1, 1, 2)

        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_2.addWidget(self.label_3, 3, 0, 1, 1)

        self.EMGchannelCombox = QComboBox(self.groupBox)
        self.EMGchannelCombox.setObjectName(u"EMGchannelCombox")

        self.gridLayout_2.addWidget(self.EMGchannelCombox, 1, 1, 1, 2)

        self.EEGChannelCombox = QComboBox(self.groupBox)
        self.EEGChannelCombox.setObjectName(u"EEGChannelCombox")

        self.gridLayout_2.addWidget(self.EEGChannelCombox, 0, 1, 1, 2)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_2.addWidget(self.label_2, 2, 0, 1, 1)

        self.label_8 = QLabel(self.groupBox)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_2.addWidget(self.label_8, 1, 0, 1, 1)

        self.EEGSiteCombox = QComboBox(self.groupBox)
        self.EEGSiteCombox.addItem("")
        self.EEGSiteCombox.addItem("")
        self.EEGSiteCombox.setObjectName(u"EEGSiteCombox")

        self.gridLayout_2.addWidget(self.EEGSiteCombox, 2, 1, 1, 2)

        self.SaveAnnoCheckbox = QCheckBox(self.groupBox)
        self.SaveAnnoCheckbox.setObjectName(u"SaveAnnoCheckbox")

        self.gridLayout_2.addWidget(self.SaveAnnoCheckbox, 4, 0, 1, 3)


        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 2)


        self.retranslateUi(AutoStageLightGBMDialog)

        QMetaObject.connectSlotsByName(AutoStageLightGBMDialog)
    # setupUi

    def retranslateUi(self, AutoStageLightGBMDialog):
        AutoStageLightGBMDialog.setWindowTitle(QCoreApplication.translate("AutoStageLightGBMDialog", u"Dialog", None))
        self.OKBt.setText(QCoreApplication.translate("AutoStageLightGBMDialog", u"Ok", None))
        self.CancelBt.setText(QCoreApplication.translate("AutoStageLightGBMDialog", u"Cancel", None))
        self.groupBox.setTitle(QCoreApplication.translate("AutoStageLightGBMDialog", u"Light GBM Auto Stage options", None))
        self.AgeCombox.setItemText(0, QCoreApplication.translate("AutoStageLightGBMDialog", u"> P56", None))
        self.AgeCombox.setItemText(1, QCoreApplication.translate("AutoStageLightGBMDialog", u"P30 - P56", None))
        self.AgeCombox.setItemText(2, QCoreApplication.translate("AutoStageLightGBMDialog", u"< P30", None))

        self.label.setText(QCoreApplication.translate("AutoStageLightGBMDialog", u"EEG channel:", None))
        self.label_3.setText(QCoreApplication.translate("AutoStageLightGBMDialog", u"Mouse age:", None))
        self.label_2.setText(QCoreApplication.translate("AutoStageLightGBMDialog", u"EEG site:", None))
        self.label_8.setText(QCoreApplication.translate("AutoStageLightGBMDialog", u"EMG channel:", None))
        self.EEGSiteCombox.setItemText(0, QCoreApplication.translate("AutoStageLightGBMDialog", u"Parietal", None))
        self.EEGSiteCombox.setItemText(1, QCoreApplication.translate("AutoStageLightGBMDialog", u"Frontal", None))

        self.SaveAnnoCheckbox.setText(QCoreApplication.translate("AutoStageLightGBMDialog", u"Cover current label", None))
    # retranslateUi

