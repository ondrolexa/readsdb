# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pysdb3/ui/addeditunit.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DialogAddEditUnit(object):
    def setupUi(self, DialogAddEditUnit):
        DialogAddEditUnit.setObjectName("DialogAddEditUnit")
        DialogAddEditUnit.setWindowModality(QtCore.Qt.ApplicationModal)
        DialogAddEditUnit.resize(260, 200)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(DialogAddEditUnit)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(DialogAddEditUnit)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.unitnameEdit = QtWidgets.QLineEdit(DialogAddEditUnit)
        self.unitnameEdit.setObjectName("unitnameEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.unitnameEdit)
        self.verticalLayout_2.addLayout(self.formLayout)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_5 = QtWidgets.QLabel(DialogAddEditUnit)
        self.label_5.setObjectName("label_5")
        self.verticalLayout.addWidget(self.label_5)
        self.descriptionEdit = QtWidgets.QPlainTextEdit(DialogAddEditUnit)
        self.descriptionEdit.setObjectName("descriptionEdit")
        self.verticalLayout.addWidget(self.descriptionEdit)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(DialogAddEditUnit)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_2.addWidget(self.buttonBox)
        self.label.setBuddy(self.unitnameEdit)
        self.label_5.setBuddy(self.descriptionEdit)

        self.retranslateUi(DialogAddEditUnit)
        self.buttonBox.accepted.connect(DialogAddEditUnit.accept)
        self.buttonBox.rejected.connect(DialogAddEditUnit.reject)
        QtCore.QMetaObject.connectSlotsByName(DialogAddEditUnit)
        DialogAddEditUnit.setTabOrder(self.unitnameEdit, self.buttonBox)
        DialogAddEditUnit.setTabOrder(self.buttonBox, self.descriptionEdit)

    def retranslateUi(self, DialogAddEditUnit):
        _translate = QtCore.QCoreApplication.translate
        DialogAddEditUnit.setWindowTitle(_translate("DialogAddEditUnit", "Add site"))
        self.label.setText(_translate("DialogAddEditUnit", "&Unit:"))
        self.label_5.setText(_translate("DialogAddEditUnit", "&Description:"))

