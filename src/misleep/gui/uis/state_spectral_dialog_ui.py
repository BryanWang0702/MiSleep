# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'state_spectral_dialog.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
    QDialog, QDoubleSpinBox, QGridLayout, QGroupBox,
    QLabel, QPushButton, QSizePolicy, QWidget)
from misleep.gui.resources import misleep_rc

class Ui_StateSpectralDialog(object):
    def setupUi(self, StateSpectralDialog):
        if not StateSpectralDialog.objectName():
            StateSpectralDialog.setObjectName(u"StateSpectralDialog")
        StateSpectralDialog.resize(400, 600)
        icon = QIcon()
        icon.addFile(u":/logo/logo.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        StateSpectralDialog.setWindowIcon(icon)
        self.gridLayout_2 = QGridLayout(StateSpectralDialog)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.OKBt = QPushButton(StateSpectralDialog)
        self.OKBt.setObjectName(u"OKBt")

        self.gridLayout_2.addWidget(self.OKBt, 2, 0, 1, 1)

        self.CancelBt = QPushButton(StateSpectralDialog)
        self.CancelBt.setObjectName(u"CancelBt")

        self.gridLayout_2.addWidget(self.CancelBt, 2, 1, 1, 1)

        self.groupBox_2 = QGroupBox(StateSpectralDialog)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout_3 = QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.StartTimeCheckBox = QCheckBox(self.groupBox_2)
        self.StartTimeCheckBox.setObjectName(u"StartTimeCheckBox")

        self.gridLayout_3.addWidget(self.StartTimeCheckBox, 0, 0, 1, 1)

        self.StartTimeEditor = QDateTimeEdit(self.groupBox_2)
        self.StartTimeEditor.setObjectName(u"StartTimeEditor")

        self.gridLayout_3.addWidget(self.StartTimeEditor, 1, 0, 1, 1)

        self.EndTimeCheckBox = QCheckBox(self.groupBox_2)
        self.EndTimeCheckBox.setObjectName(u"EndTimeCheckBox")

        self.gridLayout_3.addWidget(self.EndTimeCheckBox, 2, 0, 1, 1)

        self.HourSegmentCheckBox = QCheckBox(self.groupBox_2)
        self.HourSegmentCheckBox.setObjectName(u"HourSegmentCheckBox")

        self.gridLayout_3.addWidget(self.HourSegmentCheckBox, 4, 0, 1, 1)

        self.EndTimeEditor = QDateTimeEdit(self.groupBox_2)
        self.EndTimeEditor.setObjectName(u"EndTimeEditor")

        self.gridLayout_3.addWidget(self.EndTimeEditor, 3, 0, 1, 1)


        self.gridLayout_2.addWidget(self.groupBox_2, 0, 0, 1, 2)

        self.groupBox = QGroupBox(StateSpectralDialog)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setSpacing(10)
        self.gridLayout.setObjectName(u"gridLayout")
        self.BPLow = QDoubleSpinBox(self.groupBox)
        self.BPLow.setObjectName(u"BPLow")
        self.BPLow.setDecimals(1)
        self.BPLow.setMaximum(100000.000000000000000)
        self.BPLow.setSingleStep(0.100000000000000)
        self.BPLow.setValue(0.500000000000000)

        self.gridLayout.addWidget(self.BPLow, 4, 1, 1, 1)

        self.BPHigh = QDoubleSpinBox(self.groupBox)
        self.BPHigh.setObjectName(u"BPHigh")
        self.BPHigh.setDecimals(1)
        self.BPHigh.setMaximum(10000.000000000000000)
        self.BPHigh.setSingleStep(0.100000000000000)
        self.BPHigh.setValue(30.000000000000000)

        self.gridLayout.addWidget(self.BPHigh, 4, 2, 1, 1)

        self.ArtThresholdSpinBox = QDoubleSpinBox(self.groupBox)
        self.ArtThresholdSpinBox.setObjectName(u"ArtThresholdSpinBox")
        self.ArtThresholdSpinBox.setDecimals(1)
        self.ArtThresholdSpinBox.setValue(2.000000000000000)

        self.gridLayout.addWidget(self.ArtThresholdSpinBox, 13, 2, 1, 1)

        self.GaussianCheckBox = QCheckBox(self.groupBox)
        self.GaussianCheckBox.setObjectName(u"GaussianCheckBox")

        self.gridLayout.addWidget(self.GaussianCheckBox, 8, 0, 1, 2)

        self.MergeDataCheckBox = QCheckBox(self.groupBox)
        self.MergeDataCheckBox.setObjectName(u"MergeDataCheckBox")

        self.gridLayout.addWidget(self.MergeDataCheckBox, 14, 0, 1, 2)

        self.WinLengthCheckBox = QCheckBox(self.groupBox)
        self.WinLengthCheckBox.setObjectName(u"WinLengthCheckBox")

        self.gridLayout.addWidget(self.WinLengthCheckBox, 5, 0, 1, 2)

        self.ChannelSelector = QComboBox(self.groupBox)
        self.ChannelSelector.setObjectName(u"ChannelSelector")

        self.gridLayout.addWidget(self.ChannelSelector, 1, 0, 1, 3)

        self.RelativeCheckBox = QCheckBox(self.groupBox)
        self.RelativeCheckBox.setObjectName(u"RelativeCheckBox")

        self.gridLayout.addWidget(self.RelativeCheckBox, 12, 0, 1, 2)

        self.WinLengthSpinBox = QDoubleSpinBox(self.groupBox)
        self.WinLengthSpinBox.setObjectName(u"WinLengthSpinBox")
        self.WinLengthSpinBox.setMinimum(0.100000000000000)
        self.WinLengthSpinBox.setMaximum(100.000000000000000)
        self.WinLengthSpinBox.setSingleStep(0.100000000000000)
        self.WinLengthSpinBox.setValue(10.000000000000000)

        self.gridLayout.addWidget(self.WinLengthSpinBox, 5, 2, 1, 1)

        self.BPFilterCheckBox = QCheckBox(self.groupBox)
        self.BPFilterCheckBox.setObjectName(u"BPFilterCheckBox")

        self.gridLayout.addWidget(self.BPFilterCheckBox, 4, 0, 1, 1)

        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.RejectArtifactCheckBox = QCheckBox(self.groupBox)
        self.RejectArtifactCheckBox.setObjectName(u"RejectArtifactCheckBox")

        self.gridLayout.addWidget(self.RejectArtifactCheckBox, 13, 0, 1, 2)

        self.GaussianSpinBox = QDoubleSpinBox(self.groupBox)
        self.GaussianSpinBox.setObjectName(u"GaussianSpinBox")
        self.GaussianSpinBox.setMinimum(0.100000000000000)
        self.GaussianSpinBox.setMaximum(20.000000000000000)
        self.GaussianSpinBox.setValue(2.000000000000000)

        self.gridLayout.addWidget(self.GaussianSpinBox, 8, 2, 1, 1)

        self.nfftCheckBox = QCheckBox(self.groupBox)
        self.nfftCheckBox.setObjectName(u"nfftCheckBox")

        self.gridLayout.addWidget(self.nfftCheckBox, 6, 0, 1, 2)

        self.nfftSpinBox = QDoubleSpinBox(self.groupBox)
        self.nfftSpinBox.setObjectName(u"nfftSpinBox")
        self.nfftSpinBox.setMinimum(0.200000000000000)
        self.nfftSpinBox.setMaximum(100.000000000000000)
        self.nfftSpinBox.setValue(10.000000000000000)

        self.gridLayout.addWidget(self.nfftSpinBox, 6, 2, 1, 1)


        self.gridLayout_2.addWidget(self.groupBox, 1, 0, 1, 2)


        self.retranslateUi(StateSpectralDialog)

        QMetaObject.connectSlotsByName(StateSpectralDialog)
    # setupUi

    def retranslateUi(self, StateSpectralDialog):
        StateSpectralDialog.setWindowTitle(QCoreApplication.translate("StateSpectralDialog", u"Dialog", None))
        self.OKBt.setText(QCoreApplication.translate("StateSpectralDialog", u"OK", None))
        self.CancelBt.setText(QCoreApplication.translate("StateSpectralDialog", u"Cancel", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("StateSpectralDialog", u"Time options", None))
        self.StartTimeCheckBox.setText(QCoreApplication.translate("StateSpectralDialog", u"Start time", None))
        self.StartTimeEditor.setDisplayFormat(QCoreApplication.translate("StateSpectralDialog", u"yyyy/MM/dd HH:mm:ss", None))
        self.EndTimeCheckBox.setText(QCoreApplication.translate("StateSpectralDialog", u"Stop time", None))
        self.HourSegmentCheckBox.setText(QCoreApplication.translate("StateSpectralDialog", u"Hour segmentation", None))
        self.EndTimeEditor.setDisplayFormat(QCoreApplication.translate("StateSpectralDialog", u"yyyy/MM/dd HH:mm:ss", None))
        self.groupBox.setTitle(QCoreApplication.translate("StateSpectralDialog", u"State spectral analysis options", None))
        self.GaussianCheckBox.setText(QCoreApplication.translate("StateSpectralDialog", u"Gaussian smmothing(sigma)", None))
        self.MergeDataCheckBox.setText(QCoreApplication.translate("StateSpectralDialog", u"Merge data", None))
        self.WinLengthCheckBox.setText(QCoreApplication.translate("StateSpectralDialog", u"Window length(s)", None))
        self.RelativeCheckBox.setText(QCoreApplication.translate("StateSpectralDialog", u"Relative", None))
        self.BPFilterCheckBox.setText(QCoreApplication.translate("StateSpectralDialog", u"Bandpass filter", None))
        self.label.setText(QCoreApplication.translate("StateSpectralDialog", u"Channel:", None))
        self.RejectArtifactCheckBox.setText(QCoreApplication.translate("StateSpectralDialog", u"Reject artifact", None))
        self.nfftCheckBox.setText(QCoreApplication.translate("StateSpectralDialog", u"nfft(s, > window length)", None))
    # retranslateUi

