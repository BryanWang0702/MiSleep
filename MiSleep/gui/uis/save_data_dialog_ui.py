# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'misleep/gui/uis/save_data_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(432, 154)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.ACTimeEdit = QtWidgets.QGroupBox(Dialog)
        self.ACTimeEdit.setObjectName("ACTimeEdit")
        self.gridLayout = QtWidgets.QGridLayout(self.ACTimeEdit)
        self.gridLayout.setObjectName("gridLayout")
        self.dateTimeEdit = QtWidgets.QDateTimeEdit(self.ACTimeEdit)
        self.dateTimeEdit.setObjectName("dateTimeEdit")
        self.gridLayout.addWidget(self.dateTimeEdit, 1, 0, 1, 1)
        self.ResetACTimeEdit = QtWidgets.QCheckBox(self.ACTimeEdit)
        self.ResetACTimeEdit.setObjectName("ResetACTimeEdit")
        self.gridLayout.addWidget(self.ResetACTimeEdit, 0, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 1, 1, 1)
        self.verticalLayout.addWidget(self.ACTimeEdit)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept) # type: ignore
        self.buttonBox.rejected.connect(Dialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.ACTimeEdit.setTitle(_translate("Dialog", "Save data options"))
        self.ResetACTimeEdit.setText(_translate("Dialog", "Reset acquisition time?"))