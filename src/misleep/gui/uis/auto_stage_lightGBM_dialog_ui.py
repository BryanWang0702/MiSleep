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
    QDoubleSpinBox, QGridLayout, QGroupBox, QLabel,
    QPushButton, QSizePolicy, QWidget)
from misleep.gui.resources import misleep_rc

class Ui_AutoStageLightGBMDialog(object):
    def setupUi(self, AutoStageLightGBMDialog):
        if not AutoStageLightGBMDialog.objectName():
            AutoStageLightGBMDialog.setObjectName(u"AutoStageLightGBMDialog")
        AutoStageLightGBMDialog.resize(420, 300)
        icon = QIcon()
        icon.addFile(u":/logo/logo.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        AutoStageLightGBMDialog.setWindowIcon(icon)
        self.gridLayout = QGridLayout(AutoStageLightGBMDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.groupBox = QGroupBox(AutoStageLightGBMDialog)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_2 = QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.EEGChannelCombox = QComboBox(self.groupBox)
        self.EEGChannelCombox.setObjectName(u"EEGChannelCombox")

        self.gridLayout_2.addWidget(self.EEGChannelCombox, 0, 1, 1, 3)

        self.UseEMGCheckbox = QCheckBox(self.groupBox)
        self.UseEMGCheckbox.setObjectName(u"UseEMGCheckbox")
        self.UseEMGCheckbox.setChecked(True)

        self.gridLayout_2.addWidget(self.UseEMGCheckbox, 1, 0, 1, 1)

        self.label_8 = QLabel(self.groupBox)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_2.addWidget(self.label_8, 1, 1, 1, 1)

        self.EMGchannelCombox = QComboBox(self.groupBox)
        self.EMGchannelCombox.setObjectName(u"EMGchannelCombox")

        self.gridLayout_2.addWidget(self.EMGchannelCombox, 1, 2, 1, 2)

        self.UseACCCheckbox = QCheckBox(self.groupBox)
        self.UseACCCheckbox.setObjectName(u"UseACCCheckbox")
        self.UseACCCheckbox.setChecked(False)

        self.gridLayout_2.addWidget(self.UseACCCheckbox, 2, 0, 1, 1)

        self.label_9 = QLabel(self.groupBox)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_2.addWidget(self.label_9, 2, 1, 1, 1)

        self.ACCchannelCombox = QComboBox(self.groupBox)
        self.ACCchannelCombox.setObjectName(u"ACCchannelCombox")

        self.gridLayout_2.addWidget(self.ACCchannelCombox, 2, 2, 1, 2)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_2.addWidget(self.label_2, 3, 0, 1, 1)

        self.EEGSiteCombox = QComboBox(self.groupBox)
        self.EEGSiteCombox.addItem("")
        self.EEGSiteCombox.addItem("")
        self.EEGSiteCombox.setObjectName(u"EEGSiteCombox")

        self.gridLayout_2.addWidget(self.EEGSiteCombox, 3, 1, 1, 3)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_2.addWidget(self.label_3, 4, 0, 1, 1)

        self.AgeCombox = QComboBox(self.groupBox)
        self.AgeCombox.addItem("")
        self.AgeCombox.addItem("")
        self.AgeCombox.addItem("")
        self.AgeCombox.setObjectName(u"AgeCombox")

        self.gridLayout_2.addWidget(self.AgeCombox, 4, 1, 1, 3)

        self.label_10 = QLabel(self.groupBox)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout_2.addWidget(self.label_10, 5, 0, 1, 1)

        self.ConfidenceThresholdSpin = QDoubleSpinBox(self.groupBox)
        self.ConfidenceThresholdSpin.setObjectName(u"ConfidenceThresholdSpin")
        self.ConfidenceThresholdSpin.setDecimals(2)
        self.ConfidenceThresholdSpin.setMinimum(0.050000000000000)
        self.ConfidenceThresholdSpin.setMaximum(0.950000000000000)
        self.ConfidenceThresholdSpin.setSingleStep(0.050000000000000)
        self.ConfidenceThresholdSpin.setValue(0.800000000000000)

        self.gridLayout_2.addWidget(self.ConfidenceThresholdSpin, 5, 1, 1, 3)

        self.label_11 = QLabel(self.groupBox)
        self.label_11.setObjectName(u"label_11")

        self.gridLayout_2.addWidget(self.label_11, 6, 0, 1, 1)

        self.HMMTemperatureSpin = QDoubleSpinBox(self.groupBox)
        self.HMMTemperatureSpin.setObjectName(u"HMMTemperatureSpin")
        self.HMMTemperatureSpin.setDecimals(2)
        self.HMMTemperatureSpin.setMinimum(0.050000000000000)
        self.HMMTemperatureSpin.setMaximum(2.000000000000000)
        self.HMMTemperatureSpin.setSingleStep(0.050000000000000)
        self.HMMTemperatureSpin.setValue(0.100000000000000)

        self.gridLayout_2.addWidget(self.HMMTemperatureSpin, 6, 1, 1, 3)

        self.SaveAnnoCheckbox = QCheckBox(self.groupBox)
        self.SaveAnnoCheckbox.setObjectName(u"SaveAnnoCheckbox")
        self.SaveAnnoCheckbox.setChecked(True)

        self.gridLayout_2.addWidget(self.SaveAnnoCheckbox, 7, 0, 1, 4)


        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 2)

        self.OKBt = QPushButton(AutoStageLightGBMDialog)
        self.OKBt.setObjectName(u"OKBt")

        self.gridLayout.addWidget(self.OKBt, 1, 0, 1, 1)

        self.CancelBt = QPushButton(AutoStageLightGBMDialog)
        self.CancelBt.setObjectName(u"CancelBt")

        self.gridLayout.addWidget(self.CancelBt, 1, 1, 1, 1)


        self.retranslateUi(AutoStageLightGBMDialog)

        QMetaObject.connectSlotsByName(AutoStageLightGBMDialog)
    # setupUi

    def retranslateUi(self, AutoStageLightGBMDialog):
        AutoStageLightGBMDialog.setWindowTitle(QCoreApplication.translate("AutoStageLightGBMDialog", u"LightGBM Auto Stage", None))
        self.groupBox.setTitle(QCoreApplication.translate("AutoStageLightGBMDialog", u"Light GBM Auto Stage options", None))
        self.label.setText(QCoreApplication.translate("AutoStageLightGBMDialog", u"EEG channel:", None))
        self.UseEMGCheckbox.setText(QCoreApplication.translate("AutoStageLightGBMDialog", u"Use EMG", None))
        self.label_8.setText(QCoreApplication.translate("AutoStageLightGBMDialog", u"EMG channel:", None))
        self.UseACCCheckbox.setText(QCoreApplication.translate("AutoStageLightGBMDialog", u"Use ACC", None))
        self.label_9.setText(QCoreApplication.translate("AutoStageLightGBMDialog", u"ACC channel:", None))
        self.label_2.setText(QCoreApplication.translate("AutoStageLightGBMDialog", u"EEG site:", None))
        self.EEGSiteCombox.setItemText(0, QCoreApplication.translate("AutoStageLightGBMDialog", u"Parietal", None))
        self.EEGSiteCombox.setItemText(1, QCoreApplication.translate("AutoStageLightGBMDialog", u"Frontal", None))

        self.label_3.setText(QCoreApplication.translate("AutoStageLightGBMDialog", u"Mouse age:", None))
        self.AgeCombox.setItemText(0, QCoreApplication.translate("AutoStageLightGBMDialog", u"> P56", None))
        self.AgeCombox.setItemText(1, QCoreApplication.translate("AutoStageLightGBMDialog", u"P30 - P56", None))
        self.AgeCombox.setItemText(2, QCoreApplication.translate("AutoStageLightGBMDialog", u"< P30", None))

        self.label_10.setText(QCoreApplication.translate("AutoStageLightGBMDialog", u"Low confidence rate:", None))
        self.label_11.setText(QCoreApplication.translate("AutoStageLightGBMDialog", u"HMM T:", None))
        self.SaveAnnoCheckbox.setText(QCoreApplication.translate("AutoStageLightGBMDialog", u"Cover current label (only fills INIT states)", None))
        self.OKBt.setText(QCoreApplication.translate("AutoStageLightGBMDialog", u"Ok", None))
        self.CancelBt.setText(QCoreApplication.translate("AutoStageLightGBMDialog", u"Cancel", None))
    # retranslateUi

