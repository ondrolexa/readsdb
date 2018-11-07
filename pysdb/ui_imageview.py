# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pysdb3/ui/imageview.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DialogImageView(object):
    def setupUi(self, DialogImageView):
        DialogImageView.setObjectName("DialogImageView")
        DialogImageView.resize(640, 480)
        self.gridLayout = QtWidgets.QGridLayout(DialogImageView)
        self.gridLayout.setObjectName("gridLayout")
        self.scrollArea = QtWidgets.QScrollArea(DialogImageView)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 620, 460))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.imageLabel = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.imageLabel.sizePolicy().hasHeightForWidth())
        self.imageLabel.setSizePolicy(sizePolicy)
        self.imageLabel.setObjectName("imageLabel")
        self.gridLayout_2.addWidget(self.imageLabel, 0, 0, 1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 1)

        self.retranslateUi(DialogImageView)
        QtCore.QMetaObject.connectSlotsByName(DialogImageView)

    def retranslateUi(self, DialogImageView):
        _translate = QtCore.QCoreApplication.translate
        DialogImageView.setWindowTitle(_translate("DialogImageView", "Dialog"))
        self.imageLabel.setText(_translate("DialogImageView", "TextLabel"))

