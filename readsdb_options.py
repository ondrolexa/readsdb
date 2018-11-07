# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ReadSDBDialog
                                 A QGIS plugin
 Read PySDB structural data into QGIS
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2018-11-03
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Ondrej Lexa
        email                : lexa.ondrej@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os

from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from qgis.core import *

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/readsdb_options.ui'))


class ReadSDBOptionsDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, readsdb, parent=None):
        """Constructor."""
        super(ReadSDBOptionsDialog, self).__init__(parent, Qt.WindowStaysOnTopHint)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.btn_calc_md.clicked.connect(self.calc_md)
        self.btn_calc_gc.clicked.connect(self.calc_gc)
        self.btn_store.clicked.connect(self.store_date)
        self.readsdb = readsdb
        self.settings = self.readsdb.settings

    def accept(self):
        try:
            self.settings.setValue("angle_gc", float(self.angle_gc.text()))
            self.settings.setValue("angle_md", float(self.angle_md.text()))
            self.settings.setValue("offset", int(self.offset.text()))
            self.settings.setValue("auto_gc", bool(self.corr_gc_auto.isChecked()))
            self.settings.setValue("auto_md", bool(self.corr_md_auto.isChecked()))
            super(ReadSDBOptionsDialog, self).accept()
        except:
            QtWidgets.QMessageBox.warning(self, 'Warning', self.readsdb.tr(u'Check option values.'))

    def calc_gc(self):
        """Calculate Grid convergence at map canvas centre"""
        gc = self.readsdb.calc_gc()
        self.angle_gc.setText('{:g}'.format(gc))

    def calc_md(self):
        dec = self.readsdb.calc_md(time=self.dateEdit.date().toPyDate())
        self.angle_md.setText('{:g}'.format(dec))

    def store_date(self):
        self.readsdb.sdb.meta('measured', self.dateEdit.date().toPyDate().strftime("%d.%m.%Y %H:%M"))
        self.readsdb.iface.messageBar().pushSuccess('SDB Read', 'Date stored in SDB.')

