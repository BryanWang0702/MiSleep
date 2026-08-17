# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'spindle_detect_dialog.ui'
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
    QDoubleSpinBox, QFrame, QGridLayout, QGroupBox,
    QLabel, QPushButton, QSizePolicy, QWidget)
from misleep.gui.resources import misleep_rc

class Ui_SpindleDetectDialog(object):
    def setupUi(self, SpindleDetectDialog):
        if not SpindleDetectDialog.objectName():
            SpindleDetectDialog.setObjectName(u"SpindleDetectDialog")
        SpindleDetectDialog.resize(278, 429)
        icon = QIcon()
        icon.addFile(u":/logo/logo.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        SpindleDetectDialog.setWindowIcon(icon)
        self.gridLayout = QGridLayout(SpindleDetectDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.groupBox = QGroupBox(SpindleDetectDialog)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_2 = QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.WakeCheckbox = QCheckBox(self.groupBox)
        self.WakeCheckbox.setObjectName(u"WakeCheckbox")

        self.gridLayout_2.addWidget(self.WakeCheckbox, 12, 0, 1, 1)

        self.StdEditor = QDoubleSpinBox(self.groupBox)
        self.StdEditor.setObjectName(u"StdEditor")
        self.StdEditor.setValue(1.500000000000000)

        self.gridLayout_2.addWidget(self.StdEditor, 6, 0, 1, 1)

        self.ExportCheckbox = QCheckBox(self.groupBox)
        self.ExportCheckbox.setObjectName(u"ExportCheckbox")

        self.gridLayout_2.addWidget(self.ExportCheckbox, 14, 0, 1, 3)

        self.line = QFrame(self.groupBox)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_2.addWidget(self.line, 1, 0, 1, 3)

        self.REMCheckbox = QCheckBox(self.groupBox)
        self.REMCheckbox.setObjectName(u"REMCheckbox")

        self.gridLayout_2.addWidget(self.REMCheckbox, 11, 1, 1, 1)

        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_2.addWidget(self.label_5, 6, 1, 1, 1)

        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_2.addWidget(self.label_4, 10, 0, 1, 3)

        self.InitCheckbox = QCheckBox(self.groupBox)
        self.InitCheckbox.setObjectName(u"InitCheckbox")

        self.gridLayout_2.addWidget(self.InitCheckbox, 12, 1, 1, 1)

        self.ChannelComBox = QComboBox(self.groupBox)
        self.ChannelComBox.setObjectName(u"ChannelComBox")

        self.gridLayout_2.addWidget(self.ChannelComBox, 0, 1, 1, 2)

        self.NREMCheckbox = QCheckBox(self.groupBox)
        self.NREMCheckbox.setObjectName(u"NREMCheckbox")
        self.NREMCheckbox.setChecked(True)

        self.gridLayout_2.addWidget(self.NREMCheckbox, 11, 0, 1, 1)

        self.line_2 = QFrame(self.groupBox)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_2.addWidget(self.line_2, 4, 0, 1, 3)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_2.addWidget(self.label_2, 2, 0, 1, 3)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_2.addWidget(self.label_3, 5, 0, 1, 2)

        self.line_4 = QFrame(self.groupBox)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShape(QFrame.Shape.HLine)
        self.line_4.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_2.addWidget(self.line_4, 13, 0, 1, 3)

        self.line_3 = QFrame(self.groupBox)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_2.addWidget(self.line_3, 9, 0, 1, 3)

        self.label_6 = QLabel(self.groupBox)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_2.addWidget(self.label_6, 7, 0, 1, 3)

        self.FreqLowEditor = QDoubleSpinBox(self.groupBox)
        self.FreqLowEditor.setObjectName(u"FreqLowEditor")
        self.FreqLowEditor.setDecimals(1)
        self.FreqLowEditor.setValue(10.000000000000000)

        self.gridLayout_2.addWidget(self.FreqLowEditor, 3, 0, 1, 1)

        self.FreqHighEditor = QDoubleSpinBox(self.groupBox)
        self.FreqHighEditor.setObjectName(u"FreqHighEditor")
        self.FreqHighEditor.setDecimals(1)
        self.FreqHighEditor.setValue(15.000000000000000)

        self.gridLayout_2.addWidget(self.FreqHighEditor, 3, 1, 1, 1)

        self.durationThresholdEditor = QDoubleSpinBox(self.groupBox)
        self.durationThresholdEditor.setObjectName(u"durationThresholdEditor")
        self.durationThresholdEditor.setValue(0.200000000000000)

        self.gridLayout_2.addWidget(self.durationThresholdEditor, 8, 0, 1, 1)

        self.label_7 = QLabel(self.groupBox)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout_2.addWidget(self.label_7, 8, 1, 1, 1)


        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 2)

        self.OKBt = QPushButton(SpindleDetectDialog)
        self.OKBt.setObjectName(u"OKBt")

        self.gridLayout.addWidget(self.OKBt, 1, 0, 1, 1)

        self.CancelBt = QPushButton(SpindleDetectDialog)
        self.CancelBt.setObjectName(u"CancelBt")

        self.gridLayout.addWidget(self.CancelBt, 1, 1, 1, 1)


        self.retranslateUi(SpindleDetectDialog)

        QMetaObject.connectSlotsByName(SpindleDetectDialog)
    # setupUi

    def retranslateUi(self, SpindleDetectDialog):
        SpindleDetectDialog.setWindowTitle(QCoreApplication.translate("SpindleDetectDialog", u"Dialog", None))
        self.groupBox.setTitle(QCoreApplication.translate("SpindleDetectDialog", u"Spindle detection options", None))
        self.WakeCheckbox.setText(QCoreApplication.translate("SpindleDetectDialog", u"Wake", None))
        self.ExportCheckbox.setText(QCoreApplication.translate("SpindleDetectDialog", u"Export to csv", None))
        self.REMCheckbox.setText(QCoreApplication.translate("SpindleDetectDialog", u"REM", None))
        self.label.setText(QCoreApplication.translate("SpindleDetectDialog", u"Channel:", None))
        self.label_5.setText(QCoreApplication.translate("SpindleDetectDialog", u"* STD + MEAN", None))
        self.label_4.setText(QCoreApplication.translate("SpindleDetectDialog", u"State", None))
        self.InitCheckbox.setText(QCoreApplication.translate("SpindleDetectDialog", u"Init", None))
        self.NREMCheckbox.setText(QCoreApplication.translate("SpindleDetectDialog", u"NREM", None))
        self.label_2.setText(QCoreApplication.translate("SpindleDetectDialog", u"Frequency band:", None))
        self.label_3.setText(QCoreApplication.translate("SpindleDetectDialog", u"Spindle square power threshold:", None))
        self.label_6.setText(QCoreApplication.translate("SpindleDetectDialog", u"Spindle duration threshold", None))
        self.label_7.setText(QCoreApplication.translate("SpindleDetectDialog", u"*STD + MEAN", None))
        self.OKBt.setText(QCoreApplication.translate("SpindleDetectDialog", u"Ok", None))
        self.CancelBt.setText(QCoreApplication.translate("SpindleDetectDialog", u"Cancel", None))
    # retranslateUi

