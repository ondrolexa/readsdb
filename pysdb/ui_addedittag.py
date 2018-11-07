# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pysdb3/ui/addedittag.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DialogAddEditTag(object):
    def setupUi(self, DialogAddEditTag):
        DialogAddEditTag.setObjectName("DialogAddEditTag")
        DialogAddEditTag.setWindowModality(QtCore.Qt.ApplicationModal)
        DialogAddEditTag.resize(260, 200)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(DialogAddEditTag)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(DialogAddEditTag)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.tagnameEdit = QtWidgets.QLineEdit(DialogAddEditTag)
        self.tagnameEdit.setObjectName("tagnameEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.tagnameEdit)
        self.verticalLayout_2.addLayout(self.formLayout)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_5 = QtWidgets.QLabel(DialogAddEditTag)
        self.label_5.setObjectName("label_5")
        self.verticalLayout.addWidget(self.label_5)
        self.descriptionEdit = QtWidgets.QPlainTextEdit(DialogAddEditTag)
        self.descriptionEdit.setObjectName("descriptionEdit")
        self.verticalLayout.addWidget(self.descriptionEdit)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(DialogAddEditTag)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_2.addWidget(self.buttonBox)
        self.label.setBuddy(self.tagnameEdit)
        self.label_5.setBuddy(self.descriptionEdit)

        self.retranslateUi(DialogAddEditTag)
        self.buttonBox.accepted.connect(DialogAddEditTag.accept)
        self.buttonBox.rejected.connect(DialogAddEditTag.reject)
        QtCore.QMetaObject.connectSlotsByName(DialogAddEditTag)
        DialogAddEditTag.setTabOrder(self.tagnameEdit, self.buttonBox)
        DialogAddEditTag.setTabOrder(self.buttonBox, self.descriptionEdit)

    def retranslateUi(self, DialogAddEditTag):
        _translate = QtCore.QCoreApplication.translate
        DialogAddEditTag.setWindowTitle(_translate("DialogAddEditTag", "Add site"))
        self.label.setText(_translate("DialogAddEditTag", "&Tag:"))
        self.label_5.setText(_translate("DialogAddEditTag", "&Description:"))

