# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'horizontal_line_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QComboBox,
    QDialog, QDoubleSpinBox, QFrame, QGridLayout,
    QGroupBox, QLabel, QListView, QPushButton,
    QSizePolicy, QWidget)
from misleep.gui.resources import misleep_rc

class Ui_horizontal_line_dialog(object):
    def setupUi(self, horizontal_line_dialog):
        if not horizontal_line_dialog.objectName():
            horizontal_line_dialog.setObjectName(u"horizontal_line_dialog")
        horizontal_line_dialog.resize(376, 481)
        icon = QIcon()
        icon.addFile(u":/logo/logo.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        horizontal_line_dialog.setWindowIcon(icon)
        self.gridLayout = QGridLayout(horizontal_line_dialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.CancelBt = QPushButton(horizontal_line_dialog)
        self.CancelBt.setObjectName(u"CancelBt")

        self.gridLayout.addWidget(self.CancelBt, 2, 1, 1, 1)

        self.OKBt = QPushButton(horizontal_line_dialog)
        self.OKBt.setObjectName(u"OKBt")

        self.gridLayout.addWidget(self.OKBt, 2, 0, 1, 1)

        self.groupBox = QGroupBox(horizontal_line_dialog)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_2 = QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.line = QFrame(self.groupBox)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_2.addWidget(self.line, 1, 0, 1, 2)

        self.ChannelComboBox = QComboBox(self.groupBox)
        self.ChannelComboBox.setObjectName(u"ChannelComboBox")

        self.gridLayout_2.addWidget(self.ChannelComboBox, 0, 1, 1, 1)

        self.AddLineBt = QPushButton(self.groupBox)
        self.AddLineBt.setObjectName(u"AddLineBt")

        self.gridLayout_2.addWidget(self.AddLineBt, 9, 0, 1, 1)

        self.SelfDefineValueEditor = QDoubleSpinBox(self.groupBox)
        self.SelfDefineValueEditor.setObjectName(u"SelfDefineValueEditor")
        self.SelfDefineValueEditor.setDecimals(6)
        self.SelfDefineValueEditor.setMinimum(-1000000.000000000000000)
        self.SelfDefineValueEditor.setMaximum(1000000.000000000000000)

        self.gridLayout_2.addWidget(self.SelfDefineValueEditor, 3, 1, 1, 1)

        self.RelativeNumEditor = QDoubleSpinBox(self.groupBox)
        self.RelativeNumEditor.setObjectName(u"RelativeNumEditor")
        self.RelativeNumEditor.setDecimals(1)
        self.RelativeNumEditor.setValue(1.000000000000000)

        self.gridLayout_2.addWidget(self.RelativeNumEditor, 6, 0, 1, 1)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_2.addWidget(self.label_2, 3, 0, 1, 1)

        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.LineListView = QListView(self.groupBox)
        self.LineListView.setObjectName(u"LineListView")
        self.LineListView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.LineListView.setProperty(u"showDropIndicator", False)
        self.LineListView.setSelectionMode(QAbstractItemView.SingleSelection)

        self.gridLayout_2.addWidget(self.LineListView, 10, 0, 1, 2)

        self.UseRelativeCheckBox = QCheckBox(self.groupBox)
        self.UseRelativeCheckBox.setObjectName(u"UseRelativeCheckBox")

        self.gridLayout_2.addWidget(self.UseRelativeCheckBox, 4, 0, 1, 1)

        self.line_2 = QFrame(self.groupBox)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_2.addWidget(self.line_2, 8, 0, 1, 2)

        self.RelativeCalComboBox = QComboBox(self.groupBox)
        self.RelativeCalComboBox.addItem("")
        self.RelativeCalComboBox.addItem("")
        self.RelativeCalComboBox.setObjectName(u"RelativeCalComboBox")

        self.gridLayout_2.addWidget(self.RelativeCalComboBox, 6, 1, 1, 1)

        self.DeleteLineBt = QPushButton(self.groupBox)
        self.DeleteLineBt.setObjectName(u"DeleteLineBt")

        self.gridLayout_2.addWidget(self.DeleteLineBt, 9, 1, 1, 1)

        self.SetColorBt = QPushButton(self.groupBox)
        self.SetColorBt.setObjectName(u"SetColorBt")

        self.gridLayout_2.addWidget(self.SetColorBt, 7, 1, 1, 1)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_2.addWidget(self.label_3, 7, 0, 1, 1)


        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 2)


        self.retranslateUi(horizontal_line_dialog)

        QMetaObject.connectSlotsByName(horizontal_line_dialog)
    # setupUi

    def retranslateUi(self, horizontal_line_dialog):
        horizontal_line_dialog.setWindowTitle(QCoreApplication.translate("horizontal_line_dialog", u"Dialog", None))
        self.CancelBt.setText(QCoreApplication.translate("horizontal_line_dialog", u"Cancel", None))
        self.OKBt.setText(QCoreApplication.translate("horizontal_line_dialog", u"OK", None))
        self.groupBox.setTitle(QCoreApplication.translate("horizontal_line_dialog", u"Horizontal Line", None))
        self.AddLineBt.setText(QCoreApplication.translate("horizontal_line_dialog", u"+", None))
        self.label_2.setText(QCoreApplication.translate("horizontal_line_dialog", u"Value:", None))
        self.label.setText(QCoreApplication.translate("horizontal_line_dialog", u"Channel: ", None))
        self.UseRelativeCheckBox.setText(QCoreApplication.translate("horizontal_line_dialog", u"Use relative", None))
        self.RelativeCalComboBox.setItemText(0, QCoreApplication.translate("horizontal_line_dialog", u"Standard Deviation", None))
        self.RelativeCalComboBox.setItemText(1, QCoreApplication.translate("horizontal_line_dialog", u"Mean", None))

        self.DeleteLineBt.setText(QCoreApplication.translate("horizontal_line_dialog", u"-", None))
        self.SetColorBt.setText("")
        self.label_3.setText(QCoreApplication.translate("horizontal_line_dialog", u"Set Color:", None))
    # retranslateUi

