# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pysdb3/ui/savediscard.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SaveDiscardDialog(object):
    def setupUi(self, SaveDiscardDialog):
        SaveDiscardDialog.setObjectName("SaveDiscardDialog")
        SaveDiscardDialog.resize(312, 125)
        self.verticalLayout = QtWidgets.QVBoxLayout(SaveDiscardDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(SaveDiscardDialog)
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/icons/process-stop.svg"))
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.messageLabel = QtWidgets.QLabel(SaveDiscardDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.messageLabel.sizePolicy().hasHeightForWidth())
        self.messageLabel.setSizePolicy(sizePolicy)
        self.messageLabel.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.messageLabel.setTextFormat(QtCore.Qt.AutoText)
        self.messageLabel.setObjectName("messageLabel")
        self.horizontalLayout_2.addWidget(self.messageLabel)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.checkBox = QtWidgets.QCheckBox(SaveDiscardDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkBox.sizePolicy().hasHeightForWidth())
        self.checkBox.setSizePolicy(sizePolicy)
        self.checkBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.checkBox.setObjectName("checkBox")
        self.horizontalLayout.addWidget(self.checkBox)
        self.comboBox = QtWidgets.QComboBox(SaveDiscardDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox.sizePolicy().hasHeightForWidth())
        self.comboBox.setSizePolicy(sizePolicy)
        self.comboBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.comboBox.setObjectName("comboBox")
        self.horizontalLayout.addWidget(self.comboBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(SaveDiscardDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(SaveDiscardDialog)
        self.buttonBox.accepted.connect(SaveDiscardDialog.accept)
        self.buttonBox.rejected.connect(SaveDiscardDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SaveDiscardDialog)

    def retranslateUi(self, SaveDiscardDialog):
        _translate = QtCore.QCoreApplication.translate
        SaveDiscardDialog.setWindowTitle(_translate("SaveDiscardDialog", "Dialog"))
        self.messageLabel.setText(_translate("SaveDiscardDialog", "dialog text will be here"))
        self.checkBox.setText(_translate("SaveDiscardDialog", "CheckBox"))

from . import pysdb3_rc
