import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic

from qgis.gui import (QgsFieldComboBox, QgsMapLayerComboBox)
from qgis.core import QgsMapLayerProxyModel

from .models import *

# uic bug fix
sys.path.append(os.path.join(os.path.dirname(__file__)))

Ui_DialogAddEditData, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui/addeditdata.ui'))
Ui_DialogAddEditSite, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui/addeditsite.ui'))
Ui_DialogAddEditStructure, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui/addeditstructure.ui'))
Ui_DialogAddEditTag, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui/addedittag.ui'))
Ui_DialogAddEditUnit, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui/addeditunit.ui'))
Ui_SaveDiscardDialog, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui/savediscard.ui'))
Ui_DataFilterDialog, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui/datafilter.ui'))
Ui_SiteFilterDialog, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui/sitefilter.ui'))
Ui_DialogSDBInfo, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui/sdbinfo.ui'))
Ui_ImportLayerDialog, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui/importlayer.ui'))

class DialogAddEditSite(QtWidgets.QDialog):
    def __init__(self, model, action, data=[-1,'',0.0,0.0,'',None], parent=None):
        super(DialogAddEditSite, self).__init__(parent)

        self.ui = Ui_DialogAddEditSite()
        self.ui.setupUi(self)
        self.ui.unitCombo.setModel(model)
        self.ui.unitCombo.setModelColumn(unitcol['name'])
        # store data
        self.data = data
        # populate widgets
        if action == 'Add':
            self.ui.sitenameEdit.setText('')
            self.ui.xcoordEdit.setText('0')
            self.ui.ycoordEdit.setText('0')
            self.ui.descriptionEdit.setPlainText('')
            title = 'Add site'
        else:
            self.ui.sitenameEdit.setText(data[sitecol['name']])
            self.ui.xcoordEdit.setText(str(data[sitecol['x']]))
            self.ui.ycoordEdit.setText(str(data[sitecol['y']]))
            self.ui.descriptionEdit.setPlainText(data[sitecol['desc']])
            title = 'Edit site #%d' % data[sitecol['id']]
        # set unit
        if data[sitecol['id_units']]:
            self.ui.unitCombo.setCurrentIndex(model.id2row[data[sitecol['id_units']]])
        else:
            self.ui.unitCombo.setCurrentIndex(0)
        # set title
        self.setWindowTitle(QtWidgets.QApplication.translate("DialogAddEditSite", title))
        # set validation rules
        floatval = QtGui.QDoubleValidator()
        floatval.setNotation(QtGui.QDoubleValidator.StandardNotation)
        self.ui.xcoordEdit.setValidator(floatval)
        self.ui.ycoordEdit.setValidator(floatval)

        self.ui.sitenameEdit.setFocus()


    def accept(self):
        # add site accept check
        if self.ui.sitenameEdit.text():
            self.data[sitecol['name']] = self.ui.sitenameEdit.text()
            self.data[sitecol['x']] = float(self.ui.xcoordEdit.text())
            self.data[sitecol['y']] = float(self.ui.ycoordEdit.text())
            self.data[sitecol['desc']] = self.ui.descriptionEdit.toPlainText()
            self.data[sitecol['id_units']] = self.ui.unitCombo.model().row2id[self.ui.unitCombo.currentIndex()]
            QtWidgets.QDialog.accept(self)
        else:
            QtGui.QMessageBox.warning(self, 'Add site error', 'Sitename cannot be empty!')
            self.ui.sitenameEdit.setFocus()
            return

class DialogAddEditData(QtWidgets.QDialog):
    #datacol = {'id':0,'id_sites':1,'id_struct':2,'azi':3,'inc':4,'struct':5,'desc':6,'tags':7}
    def __init__(self, model, tags, attached, action, data=[-1,-1,None,'','','','',''], parent=None):
        super(DialogAddEditData, self).__init__(parent)
        self.ui = Ui_DialogAddEditData()
        self.ui.setupUi(self)
        self.ui.structureCombo.setModel(model)
        self.ui.structureCombo.setModelColumn(structurecol['structure'])
        # store data
        self.data = data
        # populate widgets
        if action == 'Add':
            self.ui.azimuthEdit.setText('')
            self.ui.inclinationEdit.setText('')
            self.ui.descriptionEdit.setPlainText('')
            title = 'Add data'
        else:
            self.ui.azimuthEdit.setText(str(data[datacol['azi']]))
            self.ui.inclinationEdit.setText(str(data[datacol['inc']]))
            self.ui.descriptionEdit.setPlainText(data[datacol['desc']])
            title = 'Edit record #%d' % data[datacol['id']]
        # let's add view of the data source we just created:
        self.ui.taggedView.setModel(tags)
        self.ui.taggedView.setColumnHidden(tagcol['id'], True)
        self.ui.taggedView.setColumnHidden(tagcol['name'], True)
        self.ui.taggedView.setColumnHidden(tagcol['desc'], True)
        self.ui.taggedView.resizeColumnToContents(tagcol['check'])
        # set structure
        if data[datacol['id_struct']]:
            self.ui.structureCombo.setCurrentIndex(model.id2row[data[datacol['id_struct']]])
        # set attach visibility
        self.structure_changed(self.ui.structureCombo.currentIndex())
        # populate attachCombo
        self.ui.attachCombo.addItems([item[1] for item in attached])
        # connect signals
        self.ui.structureCombo.activated.connect(self.structure_changed)
        self.ui.pushAttach.clicked.connect(self.clear_attach)
        self.ui.pushFit.clicked.connect(self.fit_lineplane)

        # set title
        self.setWindowTitle(QtWidgets.QApplication.translate("DialogAddEditData", title))
        # set validation rules
        self.azival = QtGui.QDoubleValidator(0.0,360.0,1000)
        self.azival.setNotation(QtGui.QDoubleValidator.StandardNotation)
        self.incval = QtGui.QDoubleValidator(0.0,90.0,1000)
        self.incval.setNotation(QtGui.QDoubleValidator.StandardNotation)
        self.ui.azimuthEdit.setValidator(self.azival)
        self.ui.inclinationEdit.setValidator(self.incval)

        self.ui.azimuthEdit.selectAll()
        self.ui.azimuthEdit.setFocus()

    def clear_attach(self):
        self.ui.attachCombo.setCurrentIndex(-1)

    def fit_lineplane(self):
        pass

    def structure_changed(self, row):
        if self.ui.structureCombo.model().isplanar(row):
            self.ui.attachLabel.hide()
            self.ui.attachCombo.hide()
            self.ui.pushAttach.hide()
            self.ui.pushFit.hide()
            self.ui.attachErrorLabel.hide()
        else:
            self.ui.attachLabel.show()
            self.ui.attachCombo.show()
            self.ui.pushAttach.show()
            self.ui.pushFit.show()
            self.ui.attachErrorLabel.show()

    def accept(self):
        # add data accept check
        self.data[datacol['id_struct']] = self.ui.structureCombo.model().row2id[self.ui.structureCombo.currentIndex()]
        if self.azival.validate(self.ui.azimuthEdit.text(), 0)[0] == QtGui.QValidator.Acceptable:
            self.data[datacol['azi']] = float(self.ui.azimuthEdit.text())
        else:
            QtGui.QMessageBox.warning(self, 'Add site error', 'Azimuth must be number between 0-360.')
            self.ui.azimuthEdit.setFocus()
            return
        if self.incval.validate(self.ui.inclinationEdit.text(), 0)[0] == QtGui.QValidator.Acceptable:
            self.data[datacol['inc']] = float(self.ui.inclinationEdit.text())
        else:
            QtGui.QMessageBox.warning(self, 'Add site error', 'Inclinations must be number between 0-90.')
            self.ui.inclinationEdit.setFocus()
            return
        self.data[datacol['desc']] = self.ui.descriptionEdit.toPlainText()
        QtWidgets.QDialog.accept(self)

class DialogAddEditStructure(QtWidgets.QDialog):
    #structurecol = {'id':0,'structure':1,'planar':2,'desc':3,'scode':4,'gcode':5}
    def __init__(self, action, data=[-1,'', 1, '', 0, 0], parent=None):
        super(DialogAddEditStructure, self).__init__(parent)

        self.ui = Ui_DialogAddEditStructure()
        self.ui.setupUi(self)
        # store data
        self.data = list(data)
        # populate widgets
        if action == 'Add':
            self.ui.structnameEdit.setText('')
            self.ui.scodeEdit.setText('0')
            self.ui.gcodeEdit.setText('0')
            self.ui.descriptionEdit.setPlainText('')
            self.ui.radioPlanar.setChecked(True)
            title = 'Add structure'
        else:
            self.ui.structnameEdit.setText(data[structurecol['structure']])
            self.ui.scodeEdit.setText(str(data[structurecol['scode']]))
            self.ui.gcodeEdit.setText(str(data[structurecol['gcode']]))
            self.ui.descriptionEdit.setPlainText(data[structurecol['desc']])
            if data[structurecol['planar']]:
                self.ui.radioPlanar.setChecked(True)
            else:
                self.ui.radioLinear.setChecked(True)
            title = 'Edit structure #%d' % data[structurecol['id']]
        # set title
        self.setWindowTitle(QtWidgets.QApplication.translate("DialogAddEditStructure", title))
        # set validation rules
        intval = QtGui.QIntValidator()
        self.ui.scodeEdit.setValidator(intval)
        self.ui.gcodeEdit.setValidator(intval)

        self.ui.structnameEdit.setFocus()

    def accept(self):
        # add structure accept check
        if self.ui.structnameEdit.text():
            self.data[structurecol['structure']] = self.ui.structnameEdit.text()
            self.data[structurecol['scode']] = int(self.ui.scodeEdit.text())
            self.data[structurecol['gcode']] = int(self.ui.gcodeEdit.text())
            self.data[structurecol['desc']] = self.ui.descriptionEdit.toPlainText()
            if self.ui.radioPlanar.isChecked():
                self.data[structurecol['planar']] = 1
            else:
                self.data[structurecol['planar']] = 0
            QtWidgets.QDialog.accept(self)
        else:
            QtGui.QMessageBox.warning(self, 'Add structure error', 'Structure cannot be empty!')
            self.ui.structnameEdit.setFocus()
            return

class DialogAddEditUnit(QtWidgets.QDialog):
    #unitcol = {'id':0,'name':1,'desc':2}
    def __init__(self, action, data=[-1,'', 1, '', 0, 0], parent=None):
        super(DialogAddEditUnit, self).__init__(parent)

        self.ui = Ui_DialogAddEditUnit()
        self.ui.setupUi(self)
        # store data
        self.data = list(data)
        # populate widgets
        if action == 'Add':
            self.ui.unitnameEdit.setText('')
            self.ui.descriptionEdit.setPlainText('')
            title = 'Add unit'
        else:
            self.ui.unitnameEdit.setText(data[unitcol['name']])
            self.ui.descriptionEdit.setPlainText(data[unitcol['desc']])
            title = 'Edit unit #%d' % data[unitcol['id']]
        # set title
        self.setWindowTitle(QtWidgets.QApplication.translate("DialogAddEditUnit", title))
        self.ui.unitnameEdit.setFocus()

    def accept(self):
        # add structure accept check
        if self.ui.unitnameEdit.text():
            self.data[unitcol['name']] = self.ui.unitnameEdit.text()
            self.data[unitcol['desc']] = self.ui.descriptionEdit.toPlainText()
            QtWidgets.QDialog.accept(self)
        else:
            QtGui.QMessageBox.warning(self, 'Add unit error', 'Unit name cannot be empty!')
            self.ui.unitnameEdit.setFocus()
            return

class DialogAddEditTag(QtWidgets.QDialog):
    #tagcol = {'id':0,'name':1,'desc':2,'check':3}
    def __init__(self, action, data=[-1,'', 1, '', 0, 0], parent=None):
        super(DialogAddEditTag, self).__init__(parent)

        self.ui = Ui_DialogAddEditTag()
        self.ui.setupUi(self)
        # store data
        self.data = list(data)
        # populate widgets
        if action == 'Add':
            self.ui.tagnameEdit.setText('')
            self.ui.descriptionEdit.setPlainText('')
            title = 'Add tag'
        else:
            self.ui.tagnameEdit.setText(data[tagcol['name']])
            self.ui.descriptionEdit.setPlainText(data[tagcol['desc']])
            title = 'Edit tag #%d' % data[tagcol['id']]
        # set title
        self.setWindowTitle(QtWidgets.QApplication.translate("DialogAddEditTag", title))
        self.ui.tagnameEdit.setFocus()

    def accept(self):
        # add structure accept check
        if self.ui.tagnameEdit.text():
            self.data[tagcol['name']] = self.ui.tagnameEdit.text()
            self.data[tagcol['desc']] = self.ui.descriptionEdit.toPlainText()
            QtWidgets.QDialog.accept(self)
        else:
            QtGui.QMessageBox.warning(self, 'Add tag error', 'Tag name cannot be empty!')
            self.ui.tagnameEdit.setFocus()
            return

class DialogSDBInfo(QtWidgets.QDialog):
    def __init__(self, info, crs, parent=None):
        super(DialogSDBInfo, self).__init__(parent)

        self.ui = Ui_DialogSDBInfo()
        self.ui.setupUi(self)
        self.crs = crs
        # populate widgets
        self.ui.infoEdit.setPlainText(info)
        self.ui.crsEdit.setPlainText(crs)
        self.ui.crsEdit.setFocus()

    def accept(self):
        # add structure accept check
        if self.ui.crsEdit.toPlainText():
            self.crs = self.ui.crsEdit.toPlainText().replace('\n', ' ').replace('\r', '')
            QtWidgets.QDialog.accept(self)
        else:
            QtGui.QMessageBox.warning(self, 'Database info error', 'CRS cannot be empty!')
            self.ui.crsEdit.setFocus()
            return

class DialogSaveDiscard(QtWidgets.QDialog):
    #structurecol = {'id':0,'structure':1,'planar':2,'desc':3,'scode':4,'gcode':5}
    def __init__(self, items, message, label, parent=None):
        super(DialogSaveDiscard, self).__init__(parent)

        self.ui = Ui_SaveDiscardDialog()
        self.ui.setupUi(self)
        self.ui.messageLabel.setText(message)
        self.ui.checkBox.setText(label)
        self.ui.checkBox.setChecked(False)
        self.ui.comboBox.clear()
        self.ui.comboBox.addItems(items)
        self.setWindowTitle(QtWidgets.QApplication.translate("DialogSaveDiscard", 'Delete structure'))

    def checked(self):
        return self.ui.checkBox.isChecked()

    def selected(self):
        return self.ui.comboBox.currentIndex()

    def accept(self):
        QtWidgets.QDialog.accept(self)

class DialogSiteFilter(QtWidgets.QDialog):
    def __init__(self, model, parent=None):
        super(DialogSiteFilter, self).__init__(parent)

        self.ui = Ui_SiteFilterDialog()
        self.ui.setupUi(self)
        # set unit combo
        self.ui.unitCombo.setModel(model)
        self.ui.unitCombo.setModelColumn(1)
        self.ui.unitCombo.activated.connect(self.unit_sel)
        self.ui.nameEdit.textChanged.connect(self.name_sel)

    def unit_sel(self,index):
        self.ui.radioUnit.setChecked(True)

    def name_sel(self,index):
        self.ui.radioName.setChecked(True)

    def accept(self):
        QtWidgets.QDialog.accept(self)


class DialogDataFilter(QtWidgets.QDialog):
    def __init__(self, model, parent=None):
        super(DialogDataFilter, self).__init__(parent)

        self.ui = Ui_DataFilterDialog()
        self.ui.setupUi(self)
        # set unit combo
        self.ui.structureCombo.setModel(model)
        self.ui.structureCombo.setModelColumn(1)
        self.ui.structureCombo.activated.connect(self.struct_sel)
        self.ui.nameTag.textChanged.connect(self.tag_sel)

    def struct_sel(self,index):
        self.ui.radioStructure.setChecked(True)

    def tag_sel(self,index):
        self.ui.radioTag.setChecked(True)

    def accept(self):
        QtWidgets.QDialog.accept(self)


class ImportLayerDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ImportLayerDialog, self).__init__(parent)

        self.ui = Ui_ImportLayerDialog()
        self.ui.setupUi(self)
        # set unit combo
        self.layerCombo = QgsMapLayerComboBox()
        self.layerCombo.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.ui.horizontalLayoutLayer.addWidget(self.layerCombo)
        self.siteCombo = QgsFieldComboBox()
        self.siteCombo.setAllowEmptyFieldName(False)
        self.ui.verticalLayoutRequired.addWidget(self.siteCombo)
        self.unitCombo = QgsFieldComboBox()
        self.unitCombo.setAllowEmptyFieldName(True)
        self.ui.verticalLayoutOtional.addWidget(self.unitCombo)
        self.descCombo = QgsFieldComboBox()
        self.descCombo.setAllowEmptyFieldName(True)
        self.ui.verticalLayoutOtional.addWidget(self.descCombo)

        self.layerCombo.layerChanged.connect(self.layer_changed)

    def layer_changed(self,index):
        layer = self.layerCombo.currentLayer()
        self.siteCombo.setLayer(layer)
        self.unitCombo.setLayer(layer)
        self.descCombo.setLayer(layer)

    def accept(self):
        # add site accept check
        if self.ui.sitenameEdit.text():
            self.data[sitecol['name']] = self.ui.sitenameEdit.text()
            self.data[sitecol['x']] = float(self.ui.xcoordEdit.text())
            self.data[sitecol['y']] = float(self.ui.ycoordEdit.text())
            self.data[sitecol['desc']] = self.ui.descriptionEdit.toPlainText()
            self.data[sitecol['id_units']] = self.ui.unitCombo.model().row2id[self.ui.unitCombo.currentIndex()]
            QtWidgets.QDialog.accept(self)
        else:
            QtGui.QMessageBox.warning(self, 'Add site error', 'Sitename cannot be empty!')
            self.ui.sitenameEdit.setFocus()
            return