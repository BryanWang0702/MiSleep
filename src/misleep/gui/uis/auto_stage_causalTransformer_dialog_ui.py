# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'auto_stage_causalTransformer_dialog.ui'
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

class Ui_AutoStageCausalTransformerDialog(object):
    def setupUi(self, AutoStageCausalTransformerDialog):
        if not AutoStageCausalTransformerDialog.objectName():
            AutoStageCausalTransformerDialog.setObjectName(u"AutoStageCausalTransformerDialog")
        AutoStageCausalTransformerDialog.resize(408, 342)
        icon = QIcon()
        icon.addFile(u":/logo/logo.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        AutoStageCausalTransformerDialog.setWindowIcon(icon)
        self.gridLayout = QGridLayout(AutoStageCausalTransformerDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.OKBt = QPushButton(AutoStageCausalTransformerDialog)
        self.OKBt.setObjectName(u"OKBt")

        self.gridLayout.addWidget(self.OKBt, 1, 0, 1, 1)

        self.CancelBt = QPushButton(AutoStageCausalTransformerDialog)
        self.CancelBt.setObjectName(u"CancelBt")

        self.gridLayout.addWidget(self.CancelBt, 1, 1, 1, 1)

        self.groupBox = QGroupBox(AutoStageCausalTransformerDialog)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_2 = QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.EEGChannelCombox = QComboBox(self.groupBox)
        self.EEGChannelCombox.setObjectName(u"EEGChannelCombox")

        self.gridLayout_2.addWidget(self.EEGChannelCombox, 0, 1, 1, 2)

        self.label_8 = QLabel(self.groupBox)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_2.addWidget(self.label_8, 1, 0, 1, 1)

        self.EMGchannelCombox = QComboBox(self.groupBox)
        self.EMGchannelCombox.setObjectName(u"EMGchannelCombox")

        self.gridLayout_2.addWidget(self.EMGchannelCombox, 1, 1, 1, 2)

        self.SaveAnnoCheckbox = QCheckBox(self.groupBox)
        self.SaveAnnoCheckbox.setObjectName(u"SaveAnnoCheckbox")

        self.gridLayout_2.addWidget(self.SaveAnnoCheckbox, 2, 0, 1, 3)


        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 2)


        self.retranslateUi(AutoStageCausalTransformerDialog)

        QMetaObject.connectSlotsByName(AutoStageCausalTransformerDialog)
    # setupUi

    def retranslateUi(self, AutoStageCausalTransformerDialog):
        AutoStageCausalTransformerDialog.setWindowTitle(QCoreApplication.translate("AutoStageCausalTransformerDialog", u"Dialog", None))
        self.OKBt.setText(QCoreApplication.translate("AutoStageCausalTransformerDialog", u"Ok", None))
        self.CancelBt.setText(QCoreApplication.translate("AutoStageCausalTransformerDialog", u"Cancel", None))
        self.groupBox.setTitle(QCoreApplication.translate("AutoStageCausalTransformerDialog", u"Causal Transformer Auto Stage options", None))
        self.label.setText(QCoreApplication.translate("AutoStageCausalTransformerDialog", u"EEG channel:", None))
        self.label_8.setText(QCoreApplication.translate("AutoStageCausalTransformerDialog", u"EMG channel:", None))
        self.SaveAnnoCheckbox.setText(QCoreApplication.translate("AutoStageCausalTransformerDialog", u"Cover current label", None))
    # retranslateUi

