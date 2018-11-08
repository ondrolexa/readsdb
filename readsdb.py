# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ReadSDB
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
# Import the code for the dialog
from .readsdb_connect import ReadSDBConnectDialog
from .readsdb_options import ReadSDBOptionsDialog
from .readsdb_structures import ReadSDBStructuresDialog
from .readsdb_plot import ReadSDBPlotDialog
# read geomag
from .geomag import geomag

import os
from datetime import date, datetime
from math import cos, sin, pi
from pathlib import Path
import sqlite3
from PyQt5 import uic
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QVariant, Qt, QDate
from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtWidgets import QAction
from qgis.core import *

# Initialize Qt resources from file resources.py
from .resources import *

from .pysdb.mainapp import PySDBWindow

# Need latest APSG
import sys
sys.path.insert(0, '/home/ondro/develrepo/apsg')
from apsg import *

GM = geomag.GeoMag()

structure_fields = {'name': QVariant.String,
                    'unit': QVariant.String,
                    'azi': QVariant.Double,
                    'inc': QVariant.Double,
                    'struct': QVariant.String,
                    'tags': QVariant.String,
                    'desc': QVariant.String,
                    'planar': QVariant.Int,
                    'rotate': QVariant.Double,
                    'label': QVariant.String,
                    'lbloff': QVariant.String
                    }

site_fields = {'name': QVariant.String,
               'unit': QVariant.String,
               'description': QVariant.String
               }


class ReadSDB:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # check SVG dirs
        readsdb_svg_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'svg')
        svg_paths = QgsSettings().value('svg/searchPathsForSVG')
        if readsdb_svg_path not in svg_paths:
            QgsSettings().setValue('svg/searchPathsForSVG', svg_paths + [readsdb_svg_path])
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'ReadSDB_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Get the params from last session.
        self.settings = QSettings('LX', 'readsdb')
        if self.settings.value("offset") is None:
            self.settings.setValue("offset", 0)
        if self.settings.value("angle_gc") is None:
            self.settings.setValue("angle_gc", 0)
        if self.settings.value("angle_md") is None:
            self.settings.setValue("angle_md", 0)
        if self.settings.value("sdbname") is None:
            self.settings.setValue("sdbname", "")
        if self.settings.value("auto_gc") is None:
            self.settings.setValue("auto_gc", True)
        if self.settings.value("auto_md") is None:
            self.settings.setValue("auto_md", True)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Read SDB')
        # create toolbar
        self.toolbar = self.iface.addToolBar(u'ReadSDB')
        self.toolbar.setObjectName(u'ReadSDB')

        # Create the dialogs (after translation) and keep reference
        self.connect_dlg = ReadSDBConnectDialog(self)
        self.options_dlg = ReadSDBOptionsDialog(self)
        self.structures_dlg = ReadSDBStructuresDialog(self)
        self.plot_dlg = ReadSDBPlotDialog(self)

        # Store sites layer
        self.sites_layer = None

    def check_db(self):
        try:
            self.sdb = SDB(self.settings.value("sdbname", type=str))
            self.dbok = True
            for ac in self.actions[2:]:
                ac.setEnabled(True)
        except (AssertionError, sqlite3.OperationalError):
            self.dbok = False
            for ac in self.actions[2:]:
                ac.setDisabled(True)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('ReadSDB', message)

    def res_path(self, path):
        return os.path.join(self.plugin_dir, path)

    def calc_gc(self, point=None):
        """Calculate Grid convergence for project CRS"""
        crsSrc = QgsProject.instance().crs()
        crsDst = QgsCoordinateReferenceSystem(4326)
        xform = QgsCoordinateTransform(crsSrc, crsDst, QgsProject.instance())

        if point is None:
            point = self.iface.mapCanvas().extent().center()
        point_ll = xform.transform(point, QgsCoordinateTransform.ForwardTransform)

        if point_ll.y() < 89.9:
            point_ll_shift = QgsPointXY(point_ll.x(), point_ll.y() + 0.01)
            point_north = xform.transform(point_ll_shift, QgsCoordinateTransform.ReverseTransform)
            gc = point.azimuth(point_north)
        else:
            point_ll_shift = QgsPointXY(point_ll.x(), point_ll.y() - 0.01)
            point_north = xform.transform(point_ll_shift, QgsCoordinateTransform.ReverseTransform)
            gc = point_north.azimuth(point)
        return gc

    def calc_md(self, point=None, time=date.today()):
        """Calculate magnetic declination uising Christopher Weiss geomag library.

        Adapted from the geomagc software and World Magnetic Model of the NOAA
        Satellite and Information Service, National Geophysical Data Center
        http://www.ngdc.noaa.gov/geomag/WMM/DoDWMM.shtml
        """
        crsSrc = QgsProject.instance().crs()
        crsDst = QgsCoordinateReferenceSystem(4326)
        xform = QgsCoordinateTransform(crsSrc, crsDst, QgsProject.instance())

        if point is None:
            point = self.iface.mapCanvas().extent().center()
        point_ll = xform.transform(point, QgsCoordinateTransform.ForwardTransform)

        mag = GM.GeoMag(point_ll.y(), point_ll.x(), time=time)
        return mag.dec

    def add_action(self, icon_path, text, callback,
                   enabled_flag=True, add_to_menu=True, add_to_toolbar=True,
                   status_tip=None, whats_this=None, parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToDatabaseMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/readsdb/icons/icon_sdb.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Open SDB manager'),
            callback=self.pysdb_manager,
            parent=self.iface.mainWindow())

        icon_path = ':/plugins/readsdb/icons/icon_opt.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Read SDB options'),
            callback=self.set_options,
            parent=self.iface.mainWindow())

        icon_path = ':/plugins/readsdb/icons/icon_loc.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Read sites from SDB'),
            callback=self.read_sites,
            parent=self.iface.mainWindow())

        icon_path = ':/plugins/readsdb/icons/icon_str.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Read structures from SDB'),
            callback=self.read_structures,
            parent=self.iface.mainWindow())

        icon_path = ':/plugins/readsdb/icons/icon_net.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Plot structures'),
            callback=self.plot_structures,
            parent=self.iface.mainWindow())

        # Check database and set actions
        self.check_db()

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginDatabaseMenu(
                self.tr(u'&Read SDB'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def sanitize(self, text):
        rtext = ''
        if text is not None:
            rtext = text.replace('\r\n', ' ').replace('\n', ' ')
        return rtext

    def pysdb_manager(self):
        """Run PySDB manager"""
        window = PySDBWindow()
        window.readsdb = self
        p = Path(self.settings.value("sdbname", type=str))
        if not p.is_file():
            p = None
        window.openFileSDB(False, p)
        window.show()

    def set_options(self):
        """Select database and set plugin options"""
        # show the dialog
        self.options_dlg.show()
        # populate dialog
        self.options_dlg.angle_gc.setText(self.settings.value("angle_gc", type=str))
        self.options_dlg.angle_md.setText(self.settings.value("angle_md", type=str))
        self.options_dlg.offset.setText(self.settings.value("offset", type=str))
        self.options_dlg.corr_gc_auto.setChecked(self.settings.value("auto_gc", type=bool))
        self.options_dlg.corr_md_auto.setChecked(self.settings.value("auto_md", type=bool))
        # set magnetic declination calendar
        try:
            md_time = datetime.strptime(self.sdb.meta('measured'), "%d.%m.%Y %H:%M").date()
        except ValueError:
            md_time = datetime.strptime(self.sdb.meta('created'), "%d.%m.%Y %H:%M").date()
        self.options_dlg.dateEdit.setDate(QDate(md_time.year, md_time.month, md_time.day))
        # Run the dialog event loop
        self.options_dlg.exec_()

    def create_layer(self, name, fields):
        """Create temporary point layer"""
        crs = QgsCoordinateReferenceSystem()
        proj = self.sdb.meta('crs')
        crs.createFromUserInput(proj)
        lyr_fields = QgsFields()
        lyr_fields.append(QgsField('id', QVariant.Int))
        for key in fields:
            lyr_fields.append(QgsField(key, fields[key]))
        layer = QgsMemoryProviderUtils.createMemoryLayer(name, lyr_fields, QgsWkbTypes.Point, crs)
        return layer

    def read_sites(self):
        """Read sites from SDB database"""
        if self.sites_layer not in QgsProject.instance().mapLayers().values():
            QgsApplication.instance().setOverrideCursor(QCursor(Qt.WaitCursor))

            layer = self.create_layer('Sites', site_fields)
            provider = layer.dataProvider()
            layer.startEditing()
            for ix, rec in enumerate(self.sdb.execsql(SDB._SITE_SELECT)):
                feature = QgsFeature()
                feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(rec['x'], rec['y'])))
                feature.setAttributes([ix,
                                       rec['name'],
                                       rec['unit'],
                                       self.sanitize(rec['description'])
                                       ])
                provider.addFeatures([feature])

            layer.commitChanges()
            # Style layer
            layer.loadNamedStyle(self.res_path('styles/sites.qml'))
            layer.triggerRepaint()
            # add to project
            QgsProject.instance().addMapLayer(layer)
            # store pointer
            self.sites_layer = layer

            # recursively walk back the cursor to a pointer
            while QgsApplication.instance().overrideCursor() is not None and QgsApplication.instance().overrideCursor().shape() == Qt.WaitCursor:
                QgsApplication.instance().restoreOverrideCursor()
            if layer.featureCount() > 0:
                self.iface.messageBar().pushSuccess('SDB Read', '{} sites read successfully.'.format(layer.featureCount()))
            else:
                self.iface.messageBar().pushWarning('SDB Read', 'There are no sites in database.')
        else:
            self.iface.messageBar().pushWarning('SDB Read', 'Sites layer already exists.')

    def read_structures(self):
        """Read structures from SDB"""
        # check selection in site layer
        if self.sites_layer not in QgsProject.instance().mapLayers().values():
            selected_enable = False
        else:
            if self.sites_layer.selectedFeatureCount() > 0:
                selected_enable = True
            else:
                selected_enable = False
        # show the dialog
        self.structures_dlg.show()
        # populate dialog
        self.structures_dlg.comboStructure.clear()
        self.structures_dlg.comboStructure.addItems(self.sdb.structures())
        self.structures_dlg.comboUnit.clear()
        self.structures_dlg.comboUnit.addItems(['Any'] + self.sdb.units())
        self.structures_dlg.checkAverage.setChecked(False)
        self.structures_dlg.checkSelected.setEnabled(selected_enable)
        self.structures_dlg.checkSelected.setChecked(selected_enable)
        self.structures_dlg.listTags.clear()
        self.structures_dlg.listTags.addItems(self.sdb.tags())
        # Run the dialog event loop
        result = self.structures_dlg.exec_()
        # See if OK was pressed
        if result:
            QgsApplication.instance().setOverrideCursor(QCursor(Qt.WaitCursor))

            layer_name = str(self.structures_dlg.comboStructure.currentText())
            if self.structures_dlg.checkAverage.isChecked():
                layer_name += ' averaged'

            layer = self.create_layer(layer_name, structure_fields)
            provider = layer.dataProvider()
            layer.startEditing()

            # set db->project transform
            crsSrc = layer.crs()
            crsDst = QgsProject.instance().crs()
            xform = QgsCoordinateTransform(crsSrc, crsDst, QgsProject.instance())
            # declination calculated for creation date of sdb database
            try:
                md_time = datetime.strptime(self.sdb.meta('measured'), "%d.%m.%Y %H:%M").date()
            except ValueError:
                md_time = datetime.strptime(self.sdb.meta('created'), "%d.%m.%Y %H:%M").date()

            struct = str(self.structures_dlg.comboStructure.currentText())
            layer._is_planar = int(self.sdb.is_planar(struct))
            unit = str(self.structures_dlg.comboUnit.currentText())
            if unit == 'Any':
                unit = None
            tags = [item.text() for item in self.structures_dlg.listTags.selectedItems()]

            # which sites
            if selected_enable and self.structures_dlg.checkSelected.isChecked():
                sites = [f['name'] for f in self.sites_layer.selectedFeatures()]
            else:
                sites = self.sdb.sites(structs=struct, units=unit, tags=tags)
            # get scale for label offset (linear needs more)
            off_coef = 1 if layer.customProperty('SDB_planar') else 2

            # create features from data rows
            ix = 0
            for site in sites:
                # do site select to get data
                dt = self.sdb.execsql(self.sdb._make_select(sites=site, structs=struct, units=unit, tags=tags))
                # average?
                if self.structures_dlg.checkAverage.isChecked() and len(dt) > 1:
                    g = self.sdb.group(struct, sites=site, units=unit, tags=tags)
                    rec = dict(dt[0])
                    if layer._is_planar:
                        azi, inc = g.ortensor.eigenfols[0].dd
                    else:
                        azi, inc = g.ortensor.eigenlins[0].dd
                    rec['azimuth'] = float(azi)
                    rec['inclination'] = float(inc)
                    rec['description'] = 'Averaged from {} data'.format(len(dt))
                    rec['tags'] = None
                    dt = [rec]
                # add features
                for rec in dt:
                    feature = QgsFeature()
                    point = QgsPointXY(rec['x'], rec['y'])
                    feature.setGeometry(QgsGeometry.fromPointXY(point))
                    # do possible azimuth corrections in canvas crs
                    point_canvas = xform.transform(point, QgsCoordinateTransform.ForwardTransform)
                    delta = 0
                    delta += self.calc_gc(point=point_canvas) if self.settings.value("auto_gc", type=bool) else self.settings.value("angle_gc", type=float)
                    delta += self.calc_md(point=point_canvas, time=md_time) if self.settings.value("auto_md", type=bool) else self.settings.value("angle_md", type=float)
                    rotation = rec['azimuth'] + delta
                    # calculate label offset
                    offx = off_coef * self.settings.value("offset", type=int) * sin(rotation * pi / 180.0)
                    offy = -off_coef * self.settings.value("offset", type=int) * cos(rotation * pi / 180.0)
                    atts = [ix, rec['name'], rec['unit'], rec['azimuth'], rec['inclination'],
                            rec['structure'], rec['tags'], self.sanitize(rec['description']),
                            rec['planar'], rotation, int(round(rec['inclination'])), '{},{}'.format(offx, offy)]
                    feature.setAttributes(atts)
                    provider.addFeatures([feature])
                    ix += 1

            layer.commitChanges()
            if ix > 0:
                # Style layer
                if layer._is_planar:
                    layer.loadNamedStyle(self.res_path('styles/planar.qml'))
                else:
                    layer.loadNamedStyle(self.res_path('styles/linear.qml'))
                layer.triggerRepaint()
                # add to project
                QgsProject.instance().addMapLayer(layer)
                self.iface.messageBar().pushSuccess('SDB Read', '{} structures read successfully.'.format(ix))
            else:
                self.iface.messageBar().pushSuccess('SDB Read', 'No structures found. Choose different criteria.')

            # recursively walk back the cursor to a pointer
            while QgsApplication.instance().overrideCursor() is not None and QgsApplication.instance().overrideCursor().shape() == Qt.WaitCursor:
                QgsApplication.instance().restoreOverrideCursor()

    def plot_structures(self):
        """Select database and set plugin options"""
        layers = self.iface.layerTreeView().selectedLayers()
        self.plot_dlg.tabWidget.clear()
        self.plot_dlg.data_layers = []
        idx = 0
        for layer in layers:
            if hasattr(layer, '_is_planar'):
                self.plot_dlg.data_layers.append((idx, layer))
                if layer._is_planar:
                    w = uic.loadUi(os.path.join(os.path.dirname(__file__), 'ui/widget_planar.ui'))
                else:
                    w = uic.loadUi(os.path.join(os.path.dirname(__file__), 'ui/widget_linear.ui'))
                self.plot_dlg.tabWidget.addTab(w, layer.name())
                idx += 1
        if idx > 0:
            # show the dialog
            self.plot_dlg.show()
            # prepare stereo net
            self.plot_dlg.plotnet()
            # Run the dialog event loop
            self.plot_dlg.exec_()
