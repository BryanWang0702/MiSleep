# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'misleep/gui/uis/label_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(316, 442)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/logo/logo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.CancelBt = QtWidgets.QPushButton(Dialog)
        self.CancelBt.setAutoDefault(False)
        self.CancelBt.setObjectName("CancelBt")
        self.gridLayout.addWidget(self.CancelBt, 3, 1, 1, 1)
        self.OKBt = QtWidgets.QPushButton(Dialog)
        self.OKBt.setObjectName("OKBt")
        self.gridLayout.addWidget(self.OKBt, 3, 0, 1, 1)
        self.AddBt = QtWidgets.QPushButton(Dialog)
        self.AddBt.setObjectName("AddBt")
        self.gridLayout.addWidget(self.AddBt, 1, 0, 1, 1)
        self.LabelListView = QtWidgets.QListView(Dialog)
        self.LabelListView.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
        self.LabelListView.setObjectName("LabelListView")
        self.gridLayout.addWidget(self.LabelListView, 0, 0, 1, 2)
        self.DeleteBt = QtWidgets.QPushButton(Dialog)
        self.DeleteBt.setObjectName("DeleteBt")
        self.gridLayout.addWidget(self.DeleteBt, 1, 1, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.CancelBt.setText(_translate("Dialog", "Cancel"))
        self.OKBt.setText(_translate("Dialog", "OK"))
        self.AddBt.setText(_translate("Dialog", "+"))
        self.DeleteBt.setText(_translate("Dialog", "-"))
from misleep.gui.resources import misleep