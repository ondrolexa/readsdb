# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pysdb3/ui/sdbinfo.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DialogSDBInfo(object):
    def setupUi(self, DialogSDBInfo):
        DialogSDBInfo.setObjectName("DialogSDBInfo")
        DialogSDBInfo.resize(450, 400)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(DialogSDBInfo)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_5 = QtWidgets.QLabel(DialogSDBInfo)
        self.label_5.setObjectName("label_5")
        self.verticalLayout.addWidget(self.label_5)
        self.infoEdit = QtWidgets.QPlainTextEdit(DialogSDBInfo)
        self.infoEdit.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.infoEdit.sizePolicy().hasHeightForWidth())
        self.infoEdit.setSizePolicy(sizePolicy)
        self.infoEdit.setTextInteractionFlags(QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.infoEdit.setObjectName("infoEdit")
        self.verticalLayout.addWidget(self.infoEdit)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label = QtWidgets.QLabel(DialogSDBInfo)
        self.label.setObjectName("label")
        self.verticalLayout_3.addWidget(self.label)
        self.crsEdit = QtWidgets.QPlainTextEdit(DialogSDBInfo)
        self.crsEdit.setObjectName("crsEdit")
        self.verticalLayout_3.addWidget(self.crsEdit)
        self.verticalLayout_2.addLayout(self.verticalLayout_3)
        self.buttonBox = QtWidgets.QDialogButtonBox(DialogSDBInfo)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_2.addWidget(self.buttonBox)
        self.verticalLayout_2.setStretch(0, 10)
        self.verticalLayout_2.setStretch(1, 1)
        self.verticalLayout_2.setStretch(2, 1)
        self.label_5.setBuddy(self.infoEdit)

        self.retranslateUi(DialogSDBInfo)
        self.buttonBox.accepted.connect(DialogSDBInfo.accept)
        self.buttonBox.rejected.connect(DialogSDBInfo.reject)
        QtCore.QMetaObject.connectSlotsByName(DialogSDBInfo)

    def retranslateUi(self, DialogSDBInfo):
        _translate = QtCore.QCoreApplication.translate
        DialogSDBInfo.setWindowTitle(_translate("DialogSDBInfo", "Database information"))
        self.label_5.setText(_translate("DialogSDBInfo", "Info:"))
        self.label.setText(_translate("DialogSDBInfo", "Coordinate reference system:"))

