# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pysdb3/ui/addeditsite.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DialogAddEditSite(object):
    def setupUi(self, DialogAddEditSite):
        DialogAddEditSite.setObjectName("DialogAddEditSite")
        DialogAddEditSite.setWindowModality(QtCore.Qt.ApplicationModal)
        DialogAddEditSite.resize(260, 300)
        self.gridLayout_2 = QtWidgets.QGridLayout(DialogAddEditSite)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(DialogAddEditSite)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.sitenameEdit = QtWidgets.QLineEdit(DialogAddEditSite)
        self.sitenameEdit.setObjectName("sitenameEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.sitenameEdit)
        self.label_2 = QtWidgets.QLabel(DialogAddEditSite)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.xcoordEdit = QtWidgets.QLineEdit(DialogAddEditSite)
        self.xcoordEdit.setObjectName("xcoordEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.xcoordEdit)
        self.label_3 = QtWidgets.QLabel(DialogAddEditSite)
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.ycoordEdit = QtWidgets.QLineEdit(DialogAddEditSite)
        self.ycoordEdit.setObjectName("ycoordEdit")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.ycoordEdit)
        self.label_4 = QtWidgets.QLabel(DialogAddEditSite)
        self.label_4.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.unitCombo = QtWidgets.QComboBox(DialogAddEditSite)
        self.unitCombo.setObjectName("unitCombo")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.unitCombo)
        self.gridLayout_2.addLayout(self.formLayout, 0, 0, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_5 = QtWidgets.QLabel(DialogAddEditSite)
        self.label_5.setObjectName("label_5")
        self.verticalLayout.addWidget(self.label_5)
        self.descriptionEdit = QtWidgets.QPlainTextEdit(DialogAddEditSite)
        self.descriptionEdit.setObjectName("descriptionEdit")
        self.verticalLayout.addWidget(self.descriptionEdit)
        self.gridLayout_2.addLayout(self.verticalLayout, 1, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(DialogAddEditSite)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_2.addWidget(self.buttonBox, 2, 0, 1, 1)
        self.label.setBuddy(self.sitenameEdit)
        self.label_2.setBuddy(self.xcoordEdit)
        self.label_3.setBuddy(self.ycoordEdit)
        self.label_4.setBuddy(self.unitCombo)
        self.label_5.setBuddy(self.descriptionEdit)

        self.retranslateUi(DialogAddEditSite)
        self.buttonBox.accepted.connect(DialogAddEditSite.accept)
        self.buttonBox.rejected.connect(DialogAddEditSite.reject)
        QtCore.QMetaObject.connectSlotsByName(DialogAddEditSite)
        DialogAddEditSite.setTabOrder(self.sitenameEdit, self.xcoordEdit)
        DialogAddEditSite.setTabOrder(self.xcoordEdit, self.ycoordEdit)
        DialogAddEditSite.setTabOrder(self.ycoordEdit, self.unitCombo)
        DialogAddEditSite.setTabOrder(self.unitCombo, self.buttonBox)
        DialogAddEditSite.setTabOrder(self.buttonBox, self.descriptionEdit)

    def retranslateUi(self, DialogAddEditSite):
        _translate = QtCore.QCoreApplication.translate
        DialogAddEditSite.setWindowTitle(_translate("DialogAddEditSite", "Add site"))
        self.label.setText(_translate("DialogAddEditSite", "Site &name:"))
        self.label_2.setText(_translate("DialogAddEditSite", "&X coord (Lon):"))
        self.label_3.setText(_translate("DialogAddEditSite", "&Y coord (Lat):"))
        self.label_4.setText(_translate("DialogAddEditSite", "&Unit:"))
        self.label_5.setText(_translate("DialogAddEditSite", "&Description:"))

