# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SWA_detect_dialog.ui'
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

class Ui_SWADetectDialog(object):
    def setupUi(self, SWADetectDialog):
        if not SWADetectDialog.objectName():
            SWADetectDialog.setObjectName(u"SWADetectDialog")
        SWADetectDialog.resize(266, 334)
        icon = QIcon()
        icon.addFile(u":/logo/logo.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        SWADetectDialog.setWindowIcon(icon)
        self.gridLayout = QGridLayout(SWADetectDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.groupBox = QGroupBox(SWADetectDialog)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_2 = QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.line = QFrame(self.groupBox)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_2.addWidget(self.line, 1, 0, 1, 3)

        self.FreqHighEditor = QDoubleSpinBox(self.groupBox)
        self.FreqHighEditor.setObjectName(u"FreqHighEditor")
        self.FreqHighEditor.setDecimals(1)
        self.FreqHighEditor.setValue(4.000000000000000)

        self.gridLayout_2.addWidget(self.FreqHighEditor, 3, 1, 1, 1)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_2.addWidget(self.label_2, 2, 0, 1, 3)

        self.ChannelComBox = QComboBox(self.groupBox)
        self.ChannelComBox.setObjectName(u"ChannelComBox")

        self.gridLayout_2.addWidget(self.ChannelComBox, 0, 1, 1, 2)

        self.InitCheckbox = QCheckBox(self.groupBox)
        self.InitCheckbox.setObjectName(u"InitCheckbox")

        self.gridLayout_2.addWidget(self.InitCheckbox, 10, 1, 1, 1)

        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.WakeCheckbox = QCheckBox(self.groupBox)
        self.WakeCheckbox.setObjectName(u"WakeCheckbox")

        self.gridLayout_2.addWidget(self.WakeCheckbox, 10, 0, 1, 1)

        self.REMCheckbox = QCheckBox(self.groupBox)
        self.REMCheckbox.setObjectName(u"REMCheckbox")

        self.gridLayout_2.addWidget(self.REMCheckbox, 9, 1, 1, 1)

        self.line_4 = QFrame(self.groupBox)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShape(QFrame.Shape.HLine)
        self.line_4.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_2.addWidget(self.line_4, 11, 0, 1, 3)

        self.FreqLowEditor = QDoubleSpinBox(self.groupBox)
        self.FreqLowEditor.setObjectName(u"FreqLowEditor")
        self.FreqLowEditor.setDecimals(1)
        self.FreqLowEditor.setValue(0.500000000000000)

        self.gridLayout_2.addWidget(self.FreqLowEditor, 3, 0, 1, 1)

        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_2.addWidget(self.label_4, 8, 0, 1, 3)

        self.ExportCheckbox = QCheckBox(self.groupBox)
        self.ExportCheckbox.setObjectName(u"ExportCheckbox")

        self.gridLayout_2.addWidget(self.ExportCheckbox, 12, 0, 1, 3)

        self.NREMCheckbox = QCheckBox(self.groupBox)
        self.NREMCheckbox.setObjectName(u"NREMCheckbox")
        self.NREMCheckbox.setChecked(True)

        self.gridLayout_2.addWidget(self.NREMCheckbox, 9, 0, 1, 1)

        self.line_3 = QFrame(self.groupBox)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_2.addWidget(self.line_3, 7, 0, 1, 3)

        self.StdEditor = QDoubleSpinBox(self.groupBox)
        self.StdEditor.setObjectName(u"StdEditor")
        self.StdEditor.setValue(0.800000000000000)

        self.gridLayout_2.addWidget(self.StdEditor, 6, 0, 1, 1)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_2.addWidget(self.label_3, 5, 0, 1, 2)

        self.line_2 = QFrame(self.groupBox)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_2.addWidget(self.line_2, 4, 0, 1, 3)

        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_2.addWidget(self.label_5, 6, 1, 1, 1)


        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 2)

        self.OKBt = QPushButton(SWADetectDialog)
        self.OKBt.setObjectName(u"OKBt")

        self.gridLayout.addWidget(self.OKBt, 1, 0, 1, 1)

        self.CancelBt = QPushButton(SWADetectDialog)
        self.CancelBt.setObjectName(u"CancelBt")

        self.gridLayout.addWidget(self.CancelBt, 1, 1, 1, 1)


        self.retranslateUi(SWADetectDialog)

        QMetaObject.connectSlotsByName(SWADetectDialog)
    # setupUi

    def retranslateUi(self, SWADetectDialog):
        SWADetectDialog.setWindowTitle(QCoreApplication.translate("SWADetectDialog", u"Dialog", None))
        self.groupBox.setTitle(QCoreApplication.translate("SWADetectDialog", u"SWA detection options", None))
        self.label_2.setText(QCoreApplication.translate("SWADetectDialog", u"Frequency band:", None))
        self.InitCheckbox.setText(QCoreApplication.translate("SWADetectDialog", u"Init", None))
        self.label.setText(QCoreApplication.translate("SWADetectDialog", u"Channel:", None))
        self.WakeCheckbox.setText(QCoreApplication.translate("SWADetectDialog", u"Wake", None))
        self.REMCheckbox.setText(QCoreApplication.translate("SWADetectDialog", u"REM", None))
        self.label_4.setText(QCoreApplication.translate("SWADetectDialog", u"State", None))
        self.ExportCheckbox.setText(QCoreApplication.translate("SWADetectDialog", u"Export to csv", None))
        self.NREMCheckbox.setText(QCoreApplication.translate("SWADetectDialog", u"NREM", None))
        self.label_3.setText(QCoreApplication.translate("SWADetectDialog", u"Ampliitude threshold:", None))
        self.label_5.setText(QCoreApplication.translate("SWADetectDialog", u"* STD + MEAN", None))
        self.OKBt.setText(QCoreApplication.translate("SWADetectDialog", u"Ok", None))
        self.CancelBt.setText(QCoreApplication.translate("SWADetectDialog", u"Cancel", None))
    # retranslateUi

