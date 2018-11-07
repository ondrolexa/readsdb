# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pysdb3/ui/sitefilter.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SiteFilterDialog(object):
    def setupUi(self, SiteFilterDialog):
        SiteFilterDialog.setObjectName("SiteFilterDialog")
        SiteFilterDialog.resize(280, 140)
        self.verticalLayout = QtWidgets.QVBoxLayout(SiteFilterDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(SiteFilterDialog)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.formLayout = QtWidgets.QFormLayout(self.groupBox)
        self.formLayout.setObjectName("formLayout")
        self.radioUnit = QtWidgets.QRadioButton(self.groupBox)
        self.radioUnit.setObjectName("radioUnit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.radioUnit)
        self.unitCombo = QtWidgets.QComboBox(self.groupBox)
        self.unitCombo.setObjectName("unitCombo")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.unitCombo)
        self.radioName = QtWidgets.QRadioButton(self.groupBox)
        self.radioName.setObjectName("radioName")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.radioName)
        self.nameEdit = QtWidgets.QLineEdit(self.groupBox)
        self.nameEdit.setObjectName("nameEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.nameEdit)
        self.radioNone = QtWidgets.QRadioButton(self.groupBox)
        self.radioNone.setChecked(True)
        self.radioNone.setObjectName("radioNone")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.radioNone)
        self.verticalLayout.addWidget(self.groupBox)
        self.buttonBox = QtWidgets.QDialogButtonBox(SiteFilterDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(SiteFilterDialog)
        self.buttonBox.accepted.connect(SiteFilterDialog.accept)
        self.buttonBox.rejected.connect(SiteFilterDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SiteFilterDialog)

    def retranslateUi(self, SiteFilterDialog):
        _translate = QtCore.QCoreApplication.translate
        SiteFilterDialog.setWindowTitle(_translate("SiteFilterDialog", "Site filter"))
        self.radioUnit.setText(_translate("SiteFilterDialog", "Unit is"))
        self.radioName.setText(_translate("SiteFilterDialog", "Name contain"))
        self.radioNone.setText(_translate("SiteFilterDialog", "Show all sites"))

