# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'about.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QGroupBox, QLabel,
    QLayout, QSizePolicy, QVBoxLayout, QWidget)
from misleep.gui.resources import misleep_rc

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        if not AboutDialog.objectName():
            AboutDialog.setObjectName(u"AboutDialog")
        AboutDialog.resize(480, 342)
        icon = QIcon()
        icon.addFile(u":/logo/logo.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        AboutDialog.setWindowIcon(icon)
        self.verticalLayout_2 = QVBoxLayout(AboutDialog)
        self.verticalLayout_2.setSpacing(20)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setSizeConstraint(QLayout.SetFixedSize)
        self.verticalLayout_2.setContentsMargins(40, 40, 40, 20)
        self.label_4 = QLabel(AboutDialog)
        self.label_4.setObjectName(u"label_4")

        self.verticalLayout_2.addWidget(self.label_4)

        self.groupBox = QGroupBox(AboutDialog)
        self.groupBox.setObjectName(u"groupBox")
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setPointSize(11)
        self.groupBox.setFont(font)
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.VersionLabel = QLabel(self.groupBox)
        self.VersionLabel.setObjectName(u"VersionLabel")

        self.verticalLayout.addWidget(self.VersionLabel)

        self.UpdateLabel = QLabel(self.groupBox)
        self.UpdateLabel.setObjectName(u"UpdateLabel")

        self.verticalLayout.addWidget(self.UpdateLabel)

        self.CopyrightLabel = QLabel(self.groupBox)
        self.CopyrightLabel.setObjectName(u"CopyrightLabel")

        self.verticalLayout.addWidget(self.CopyrightLabel)


        self.verticalLayout_2.addWidget(self.groupBox)


        self.retranslateUi(AboutDialog)

        QMetaObject.connectSlotsByName(AboutDialog)
    # setupUi

    def retranslateUi(self, AboutDialog):
        AboutDialog.setWindowTitle(QCoreApplication.translate("AboutDialog", u"About", None))
        self.label_4.setText(QCoreApplication.translate("AboutDialog", u"<html><head/><body><p><img src=\":/logo/entire_logo.png\"/></p></body></html>", None))
        self.groupBox.setTitle(QCoreApplication.translate("AboutDialog", u"MiSleep", None))
        self.VersionLabel.setText(QCoreApplication.translate("AboutDialog", u"Version: 0.0.1", None))
        self.UpdateLabel.setText(QCoreApplication.translate("AboutDialog", u"Update: 2024/03/08", None))
        self.CopyrightLabel.setText(QCoreApplication.translate("AboutDialog", u"Copyright \u00a9 2023\u20132026 Xueqiang Wang.", None))
    # retranslateUi

