# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pysdb3/ui/datafilter.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DataFilterDialog(object):
    def setupUi(self, DataFilterDialog):
        DataFilterDialog.setObjectName("DataFilterDialog")
        DataFilterDialog.resize(280, 140)
        self.verticalLayout = QtWidgets.QVBoxLayout(DataFilterDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(DataFilterDialog)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.formLayout = QtWidgets.QFormLayout(self.groupBox)
        self.formLayout.setObjectName("formLayout")
        self.radioStructure = QtWidgets.QRadioButton(self.groupBox)
        self.radioStructure.setObjectName("radioStructure")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.radioStructure)
        self.structureCombo = QtWidgets.QComboBox(self.groupBox)
        self.structureCombo.setObjectName("structureCombo")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.structureCombo)
        self.radioTag = QtWidgets.QRadioButton(self.groupBox)
        self.radioTag.setObjectName("radioTag")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.radioTag)
        self.nameTag = QtWidgets.QLineEdit(self.groupBox)
        self.nameTag.setObjectName("nameTag")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.nameTag)
        self.radioNone = QtWidgets.QRadioButton(self.groupBox)
        self.radioNone.setChecked(True)
        self.radioNone.setObjectName("radioNone")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.radioNone)
        self.verticalLayout.addWidget(self.groupBox)
        self.buttonBox = QtWidgets.QDialogButtonBox(DataFilterDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(DataFilterDialog)
        self.buttonBox.accepted.connect(DataFilterDialog.accept)
        self.buttonBox.rejected.connect(DataFilterDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(DataFilterDialog)

    def retranslateUi(self, DataFilterDialog):
        _translate = QtCore.QCoreApplication.translate
        DataFilterDialog.setWindowTitle(_translate("DataFilterDialog", "Data filter"))
        self.radioStructure.setText(_translate("DataFilterDialog", "Structure is"))
        self.radioTag.setText(_translate("DataFilterDialog", "Tags contain"))
        self.radioNone.setText(_translate("DataFilterDialog", "Show all data"))

