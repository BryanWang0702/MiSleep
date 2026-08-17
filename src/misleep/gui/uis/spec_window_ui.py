# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'spec_window.ui'
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QGridLayout, QGroupBox,
    QLabel, QMainWindow, QPushButton, QScrollArea,
    QSizePolicy, QStatusBar, QWidget)
from misleep.gui.resources import misleep_rc

class Ui_spec_window(object):
    def setupUi(self, spec_window):
        if not spec_window.objectName():
            spec_window.setObjectName(u"spec_window")
        spec_window.resize(932, 900)
        spec_window.setMinimumSize(QSize(860, 800))
        icon = QIcon()
        icon.addFile(u":/logo/logo.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        spec_window.setWindowIcon(icon)
        self.centralwidget = QWidget(spec_window)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.formLayout = QFormLayout(self.groupBox)
        self.formLayout.setObjectName(u"formLayout")
        self.SpectrumSaveBt = QPushButton(self.groupBox)
        self.SpectrumSaveBt.setObjectName(u"SpectrumSaveBt")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.SpectrumSaveBt)

        self.DeltaThetaRatioLabel = QLabel(self.groupBox)
        self.DeltaThetaRatioLabel.setObjectName(u"DeltaThetaRatioLabel")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.DeltaThetaRatioLabel)

        self.SpectrumScrollArea = QScrollArea(self.groupBox)
        self.SpectrumScrollArea.setObjectName(u"SpectrumScrollArea")
        self.SpectrumScrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 892, 364))
        self.SpectrumScrollArea.setWidget(self.scrollAreaWidgetContents)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.SpanningRole, self.SpectrumScrollArea)


        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)

        self.groupBox_2 = QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.formLayout_2 = QFormLayout(self.groupBox_2)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.SpectrogramScrollArea = QScrollArea(self.groupBox_2)
        self.SpectrogramScrollArea.setObjectName(u"SpectrogramScrollArea")
        self.SpectrogramScrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 892, 364))
        self.SpectrogramScrollArea.setWidget(self.scrollAreaWidgetContents_2)

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.SpanningRole, self.SpectrogramScrollArea)

        self.SpectrogramSaveBt = QPushButton(self.groupBox_2)
        self.SpectrogramSaveBt.setObjectName(u"SpectrogramSaveBt")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.SpectrogramSaveBt)


        self.gridLayout.addWidget(self.groupBox_2, 1, 0, 1, 1)

        spec_window.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(spec_window)
        self.statusbar.setObjectName(u"statusbar")
        spec_window.setStatusBar(self.statusbar)

        self.retranslateUi(spec_window)

        QMetaObject.connectSlotsByName(spec_window)
    # setupUi

    def retranslateUi(self, spec_window):
        spec_window.setWindowTitle(QCoreApplication.translate("spec_window", u"Spectrum and spectrogram window", None))
        self.groupBox.setTitle(QCoreApplication.translate("spec_window", u"Spectrum", None))
        self.SpectrumSaveBt.setText(QCoreApplication.translate("spec_window", u"Save", None))
        self.DeltaThetaRatioLabel.setText(QCoreApplication.translate("spec_window", u"Delta/Theta ratio: ", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("spec_window", u"Spectrogram", None))
        self.SpectrogramSaveBt.setText(QCoreApplication.translate("spec_window", u"Save", None))
    # retranslateUi

