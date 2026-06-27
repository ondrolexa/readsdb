# -*- coding: utf-8 -*-

# ----------------------------------------------------------
# ReadSDB QGIS Plugin
# Copyright (C) 2026 Ondrej Lexa
# ----------------------------------------------------------
# Licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# --------------------------------------------------------------------

import os
import sqlite3
import sys
from datetime import date, datetime
from math import cos, pi, sin
from pathlib import Path

from qgis.core import (
    Qgis,
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeature,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsMemoryProviderUtils,
    QgsPointXY,
    QgsProject,
    QgsSettings,
    QgsWkbTypes,
)
from qgis.gui import QgsMapToolIdentifyFeature, QgsProjectionSelectionDialog
from qgis.PyQt import uic
from qgis.PyQt.QtCore import (
    QCoreApplication,
    QDate,
    QLocale,
    QSettings,
    Qt,
    QTranslator,
    QVariant,
)
from qgis.PyQt.QtGui import QCursor, QDoubleValidator, QIcon
from qgis.PyQt.QtSql import (
    QSqlDatabase,
    QSqlQuery,
    QSqlQueryModel,
    QSqlRelation,
    QSqlRelationalDelegate,
    QSqlRelationalTableModel,
    QSqlTableModel,
)
from qgis.PyQt.QtWidgets import (
    QAbstractItemView,
    QAction,
    QDataWidgetMapper,
    QDialogButtonBox,
    QFileDialog,
    QHeaderView,
    QMessageBox,
)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# import included packages
from apsg import folset, linset
from geomag import geomag

# project
from readsdb.__about__ import (
    DIR_PLUGIN_ROOT,
    __title__,
)
from readsdb.toolbelt import PlgLogger

# Import the code for the dialog
from .readsdb_import import ReadSDBImportLayer
from .readsdb_open import SDB_SELECT, ReadSDBOpenDialog
from .readsdb_options import ReadSDBOptionsDialog
from .readsdb_plot import ReadSDBPlotDialog
from .readsdb_structures import ReadSDBStructuresDialog

# Initialize Qt resources from file resources.py
from .resources import qt_version

SDB_VERSION = "3.3.0"

SCHEMA_NEW = """pragma auto_vacuum=0;
pragma default_cache_size=2000;
pragma encoding='UTF-8';
pragma page_size=1024;
drop table if exists sites;
BEGIN TRANSACTION;
DROP TABLE IF EXISTS "meta";
CREATE TABLE meta (id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(16) NOT NULL UNIQUE, value TEXT);
DROP TABLE IF EXISTS "structype";
CREATE TABLE structype (id INTEGER PRIMARY KEY AUTOINCREMENT, pos INTEGER NOT NULL DEFAULT 0, structure VARCHAR(16) NOT NULL UNIQUE, description TEXT, structcode INTEGER DEFAULT 0, groupcode INTEGER DEFAULT 0, planar INTEGER DEFAULT 1);
DROP TABLE IF EXISTS "tags";
CREATE TABLE tags (id INTEGER PRIMARY KEY AUTOINCREMENT, pos INTEGER NOT NULL DEFAULT 0, name VARCHAR(16) NOT NULL UNIQUE, description TEXT);
DROP TABLE IF EXISTS "units";
CREATE TABLE units (id INTEGER PRIMARY KEY AUTOINCREMENT, pos INTEGER NOT NULL DEFAULT 0, name VARCHAR(60) NOT NULL UNIQUE, description TEXT);
DROP TABLE IF EXISTS "sites";
CREATE TABLE sites (id INTEGER PRIMARY KEY AUTOINCREMENT, id_units INTEGER NOT NULL, name VARCHAR(16) NOT NULL UNIQUE, x_coord FLOAT DEFAULT NULL, y_coord FLOAT DEFAULT NULL, description TEXT, FOREIGN KEY (id_units) REFERENCES units(id));
DROP TABLE IF EXISTS "structdata";
CREATE TABLE structdata (id INTEGER PRIMARY KEY AUTOINCREMENT, id_sites INTEGER NOT NULL, id_structype INTEGER NOT NULL, azimuth FLOAT NOT NULL DEFAULT 0, inclination FLOAT NOT NULL DEFAULT 0, description TEXT, FOREIGN KEY (id_sites) REFERENCES sites(id), FOREIGN KEY (id_structype) REFERENCES structype(id));
DROP TABLE IF EXISTS "tagged";
CREATE TABLE tagged (id INTEGER PRIMARY KEY AUTOINCREMENT, id_tags INTEGER NOT NULL, id_structdata INTEGER NOT NULL, FOREIGN KEY (id_tags) REFERENCES tags(id), FOREIGN KEY (id_structdata) REFERENCES structdata(id));
DROP TABLE IF EXISTS "attach";
CREATE TABLE attach (id INTEGER PRIMARY KEY AUTOINCREMENT, id_structdata_planar INTEGER NOT NULL, id_structdata_linear INTEGER NOT NULL, FOREIGN KEY (id_structdata_planar) REFERENCES structdata(id) ON DELETE CASCADE, FOREIGN KEY (id_structdata_linear) REFERENCES structdata(id) ON DELETE CASCADE);
DROP INDEX IF EXISTS "ix_sites_id_units";
CREATE INDEX ix_sites_id_units ON sites (id_units);
DROP INDEX IF EXISTS "ix_structdata_id_sites";
CREATE INDEX ix_structdata_id_sites ON structdata (id_sites);
DROP INDEX IF EXISTS "ix_structdata_id_structype";
CREATE INDEX ix_structdata_id_structype ON structdata (id_structype);
DROP INDEX IF EXISTS "ix_tagged_id_tags";
CREATE INDEX ix_tagged_id_tags ON tagged (id_tags);
DROP INDEX IF EXISTS "ix_tagged_id_structdata";
CREATE INDEX ix_tagged_id_structdata ON tagged (id_structdata);
DROP INDEX IF EXISTS "ix_attach_id_structdata_linear";
CREATE INDEX ix_attach_id_structdata_linear ON attach (id_structdata_linear);
DROP INDEX IF EXISTS "ix_attach_id_structdata_planar";
CREATE INDEX ix_attach_id_structdata_planar ON attach (id_structdata_planar);
INSERT INTO structype VALUES (1, 1,'S', 'Default planar feature', 35, 13, 1);
INSERT INTO structype VALUES (2, 2, 'L', 'Default linear feature', 78, 13, 0);
INSERT INTO units VALUES (1, 1, 'Default', 'Default unit');
COMMIT;"""

GM = geomag.GeoMag()

structure_fields = {
    "name": QVariant.String,
    "unit": QVariant.String,
    "azi": QVariant.Double,
    "inc": QVariant.Double,
    "struct": QVariant.String,
    "tags": QVariant.String,
    "desc": QVariant.String,
    "planar": QVariant.Int,
    "rotate": QVariant.Double,
    "label": QVariant.String,
    "lbloff": QVariant.String,
}

site_fields = {
    "id": QVariant.Int,
    "name": QVariant.String,
    "unit": QVariant.String,
    "description": QVariant.String,
}


def sdb_make_select(structs=None, sites=None, units=None, tags=None):
    w = []
    params = []
    if structs:
        if isinstance(structs, str):
            w.append("structype.structure = ?")
            params.append(structs)
        elif isinstance(structs, (list, tuple)):
            w.append(
                "(" + " OR ".join(["structype.structure = ?" for _ in structs]) + ")"
            )
            params.extend(structs)
        else:
            raise ValueError("Keyword structs must be list or string.")
    if sites:
        if isinstance(sites, str):
            w.append("sites.name = ?")
            params.append(sites)
        elif isinstance(sites, (list, tuple)):
            w.append("(" + " OR ".join(["sites.name = ?" for _ in sites]) + ")")
            params.extend(sites)
        else:
            raise ValueError("Keyword sites must be list or string.")
    if units:
        if isinstance(units, str):
            w.append("unit = ?")
            params.append(units)
        elif isinstance(units, (list, tuple)):
            w.append("(" + " OR ".join(["unit = ?" for _ in units]) + ")")
            params.extend(units)
        else:
            raise ValueError("Keyword units must be list or string.")
    if tags:
        if isinstance(tags, str):
            tagw = ["tags LIKE ?"]
            tag_params = ["%{}%".format(tags)]
        elif isinstance(tags, (list, tuple)):
            tagw = ["(" + " AND ".join(["tags LIKE ?" for _ in tags]) + ")"]
            tag_params = ["%{}%".format(tag) for tag in tags]
        else:
            raise ValueError("Keyword tags must be list or string.")
        insel = SDB_SELECT
        if w:
            insel += " WHERE {} GROUP BY structdata.id".format(" AND ".join(w))
        else:
            insel += " GROUP BY structdata.id"
        sel = "SELECT * FROM ({}) WHERE {}".format(insel, " AND ".join(tagw))
        params.extend(tag_params)
    else:
        sel = SDB_SELECT
        if w:
            sel += " WHERE {} GROUP BY structdata.id".format(" AND ".join(w))
        else:
            sel += " GROUP BY structdata.id"
    return sel, params


def restore_cursor():
    while (
        QgsApplication.instance().overrideCursor() is not None
        and QgsApplication.instance().overrideCursor().shape()
        == Qt.CursorShape.WaitCursor
    ):
        QgsApplication.instance().restoreOverrideCursor()


# ##################################
# ########## Classes ###############
# ##################################


class ReadSDBPlugin:
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
        # logger
        self.log = PlgLogger().log
        # translation
        # initialize the locale
        self.locale: str = QgsSettings().value("locale/userLocale", QLocale().name())[
            0:2
        ]
        locale_path: Path = (
            DIR_PLUGIN_ROOT
            / "resources"
            / "i18n"
            / f"{__title__.lower()}_{self.locale}.qm"
        )
        self.log(
            message=f"Translation: {self.locale}, {locale_path}",
            log_level=Qgis.MessageLevel.NoLevel,
        )
        if locale_path.exists():
            self.translator = QTranslator()
            self.translator.load(str(locale_path.resolve()))
            QCoreApplication.installTranslator(self.translator)
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # check SVG dirs
        readsdb_svg_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "svg"
        )
        svg_paths = QgsSettings().value("svg/searchPathsForSVG")
        if svg_paths is None:
            QgsSettings().setValue("svg/searchPathsForSVG", [readsdb_svg_path])
        elif isinstance(svg_paths, str):
            QgsSettings().setValue(
                "svg/searchPathsForSVG", [svg_paths, readsdb_svg_path]
            )
        else:
            if readsdb_svg_path not in svg_paths:
                svg_paths.append(readsdb_svg_path)
                QgsSettings().setValue("svg/searchPathsForSVG", svg_paths)
        # initialize locale
        if QSettings().value("locale/userLocale"):
            locale = QSettings().value("locale/userLocale")[0:2]
            locale_path = os.path.join(
                self.plugin_dir, "i18n", "ReadSDB_{}.qm".format(locale)
            )

            if os.path.exists(locale_path):
                self.translator = QTranslator()
                self.translator.load(locale_path)

                if ".".join(qt_version) > "4.3.3":
                    QCoreApplication.installTranslator(self.translator)

        # Get the params from last session.
        self.settings = QSettings("LX", "readsdb")
        if self.settings.value("offset") is None:
            self.settings.setValue("offset", 3.5)
        if self.settings.value("linmulti") is None:
            self.settings.setValue("linmulti", 1.7)
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
        self.menu = self.tr("&Read SDB")
        # create toolbar
        self.toolbar = self.iface.addToolBar("ReadSDB")
        self.toolbar.setObjectName("ReadSDB")
        # create manager dialog
        self.manager = uic.loadUi(
            os.path.join(os.path.dirname(__file__), "ui/dock_manager.ui")
        )

        # Create the dialogs (after translation) and keep reference
        self.open_dlg = ReadSDBOpenDialog(self)
        self.options_dlg = ReadSDBOptionsDialog(self)
        self.structures_dlg = ReadSDBStructuresDialog(self)
        self.plot_dlg = ReadSDBPlotDialog(self)

        # logging
        self.log = QgsApplication.messageLog()
        self.bar = self.iface.messageBar()

        QgsProject.instance().layerStore().layerRemoved.connect(self.check_site_layer)

        # Store sites layer
        self.dbok = False
        self.sites_layer = None
        self._dirty = False

    def check_db(self):
        try:
            p = Path(self.settings.value("sdbname", type=str))
            if not p.is_file():
                raise FileNotFoundError
            if not hasattr(self, "db") or not self.db.isValid():
                if hasattr(self, "db") and self.db.isValid():
                    self.db.close()
                    QSqlDatabase.removeDatabase("readsdb_main")
                self.db = QSqlDatabase.addDatabase("QSQLITE", "readsdb_main")
            self.db.setDatabaseName(str(p))
            self.db.open()
            self.query = QSqlQuery(self.db)
            # Check tables and relations
            self.query.exec(
                "SELECT sites.name as name, sites.x_coord as x, sites.y_coord as y, units.name as unit, structdata.azimuth as azimuth, structdata.inclination as inclination, structype.structure as structure, structype.planar as planar, structdata.description as description, GROUP_CONCAT(tags.name) AS tags FROM structdata INNER JOIN sites ON structdata.id_sites=sites.id INNER JOIN structype ON structype.id = structdata.id_structype INNER JOIN units ON units.id = sites.id_units LEFT OUTER JOIN tagged ON structdata.id = tagged.id_structdata LEFT OUTER JOIN tags ON tags.id = tagged.id_tags GROUP BY structdata.id LIMIT 1"
            )
            self.query.exec("SELECT * FROM attach LIMIT 1")
            self.db.transaction()
            # Site model and view
            self.sitemodel = QSqlRelationalTableModel(db=self.db)
            self.sitemodel.setTable("sites")
            self.sitemodel.setRelation(1, QSqlRelation("units", "id", "name"))
            self.sitemodel.setHeaderData(0, Qt.Orientation.Horizontal, "ID")
            self.sitemodel.setHeaderData(1, Qt.Orientation.Horizontal, "Unit")
            self.sitemodel.setHeaderData(2, Qt.Orientation.Horizontal, "Name")
            self.sitemodel.setHeaderData(3, Qt.Orientation.Horizontal, "X")
            self.sitemodel.setHeaderData(4, Qt.Orientation.Horizontal, "Y")
            self.sitemodel.setHeaderData(5, Qt.Orientation.Horizontal, "Description")
            self.sitemodel.select()
            self.manager.siteView.setModel(self.sitemodel)
            self.manager.siteView.setItemDelegate(
                QSqlRelationalDelegate(self.manager.siteView)
            )
            self.manager.siteView.setSelectionBehavior(
                QAbstractItemView.SelectionBehavior.SelectRows
            )
            self.manager.siteView.setSelectionMode(
                QAbstractItemView.SelectionMode.SingleSelection
            )
            self.manager.siteView.hideColumn(0)
            self.manager.siteView.hideColumn(1)
            self.manager.siteView.hideColumn(3)
            self.manager.siteView.hideColumn(4)
            self.manager.siteView.hideColumn(5)
            self.manager.siteView.horizontalHeader().setSectionResizeMode(
                2, QHeaderView.ResizeMode.Stretch
            )
            self.manager.siteView.verticalHeader().setVisible(False)
            # Data model and view
            self.datamodel = QSqlRelationalTableModel(db=self.db)
            self.datamodel.setTable("structdata")
            self.datamodel.setRelation(2, QSqlRelation("structype", "id", "structure"))
            self.datamodel.setHeaderData(0, Qt.Orientation.Horizontal, "ID")
            self.datamodel.setHeaderData(1, Qt.Orientation.Horizontal, "ID_Site")
            self.datamodel.setHeaderData(2, Qt.Orientation.Horizontal, "Structure")
            self.datamodel.setHeaderData(3, Qt.Orientation.Horizontal, "Azi")
            self.datamodel.setHeaderData(4, Qt.Orientation.Horizontal, "Inc")
            self.datamodel.setHeaderData(5, Qt.Orientation.Horizontal, "Description")
            self.datamodel.setFilter("structdata.id_sites=0")
            self.datamodel.select()
            self.datamodel.relationModel(2).sort(1, Qt.SortOrder.AscendingOrder)
            self.manager.dataView.setModel(self.datamodel)
            self.manager.dataView.setItemDelegate(
                QSqlRelationalDelegate(self.manager.dataView)
            )
            self.manager.dataView.hideColumn(0)
            self.manager.dataView.hideColumn(1)
            self.manager.dataView.horizontalHeader().setSectionResizeMode(
                5, QHeaderView.ResizeMode.Stretch
            )
            self.manager.dataView.verticalHeader().setVisible(False)
            # Unit model and view
            self.unitmodel = QSqlTableModel(db=self.db)
            self.unitmodel.setTable("units")
            self.unitmodel.setHeaderData(0, Qt.Orientation.Horizontal, "ID")
            self.unitmodel.setHeaderData(1, Qt.Orientation.Horizontal, "Position")
            self.unitmodel.setHeaderData(2, Qt.Orientation.Horizontal, "Name")
            self.unitmodel.setHeaderData(3, Qt.Orientation.Horizontal, "Description")
            self.unitmodel.select()
            self.manager.unitView.setModel(self.unitmodel)
            self.manager.unitView.setSelectionBehavior(
                QAbstractItemView.SelectionBehavior.SelectRows
            )
            self.manager.unitView.setSelectionMode(
                QAbstractItemView.SelectionMode.SingleSelection
            )
            self.manager.unitView.hideColumn(0)
            self.manager.unitView.hideColumn(1)
            self.manager.unitView.horizontalHeader().setSectionResizeMode(
                3, QHeaderView.ResizeMode.Stretch
            )
            self.manager.unitView.verticalHeader().setVisible(False)
            self.manager.comboUnit.setModel(self.unitmodel)
            self.manager.comboUnit.setModelColumn(self.unitmodel.fieldIndex("name"))
            # Structures model and view
            self.structmodel = QSqlTableModel(db=self.db)
            self.structmodel.setTable("structype")
            self.structmodel.setHeaderData(0, Qt.Orientation.Horizontal, "ID")
            self.structmodel.setHeaderData(1, Qt.Orientation.Horizontal, "Position")
            self.structmodel.setHeaderData(2, Qt.Orientation.Horizontal, "Structure")
            self.structmodel.setHeaderData(3, Qt.Orientation.Horizontal, "Description")
            self.structmodel.setHeaderData(4, Qt.Orientation.Horizontal, "Structcode")
            self.structmodel.setHeaderData(5, Qt.Orientation.Horizontal, "Groupcode")
            self.structmodel.setHeaderData(6, Qt.Orientation.Horizontal, "Planar")
            self.structmodel.setSort(1, Qt.SortOrder.AscendingOrder)
            self.structmodel.select()
            self.manager.structuresView.setModel(self.structmodel)
            self.manager.structuresView.setSelectionBehavior(
                QAbstractItemView.SelectionBehavior.SelectRows
            )
            self.manager.structuresView.setSelectionMode(
                QAbstractItemView.SelectionMode.SingleSelection
            )
            self.manager.structuresView.hideColumn(0)
            self.manager.structuresView.hideColumn(1)
            self.manager.structuresView.horizontalHeader().setSectionResizeMode(
                3, QHeaderView.ResizeMode.Stretch
            )
            self.manager.structuresView.verticalHeader().setVisible(False)
            # Tags model and view
            self.tagsmodel = QSqlTableModel(db=self.db)
            self.tagsmodel.setTable("tags")
            self.tagsmodel.setHeaderData(0, Qt.Orientation.Horizontal, "ID")
            self.tagsmodel.setHeaderData(1, Qt.Orientation.Horizontal, "Position")
            self.tagsmodel.setHeaderData(2, Qt.Orientation.Horizontal, "Name")
            self.tagsmodel.setHeaderData(3, Qt.Orientation.Horizontal, "Description")
            self.tagsmodel.select()
            self.manager.tagsView.setModel(self.tagsmodel)
            self.manager.tagsView.setSelectionBehavior(
                QAbstractItemView.SelectionBehavior.SelectRows
            )
            self.manager.tagsView.setSelectionMode(
                QAbstractItemView.SelectionMode.SingleSelection
            )
            self.manager.tagsView.hideColumn(0)
            self.manager.tagsView.hideColumn(1)
            self.manager.tagsView.horizontalHeader().setSectionResizeMode(
                3, QHeaderView.ResizeMode.Stretch
            )
            self.manager.tagsView.verticalHeader().setVisible(False)
            # Meta model and view
            self.metamodel = QSqlQueryModel()
            self.metamodel.setQuery("SELECT * from meta", self.db)
            self.metamodel.setHeaderData(0, Qt.Orientation.Horizontal, "ID")
            self.metamodel.setHeaderData(1, Qt.Orientation.Horizontal, "Name")
            self.metamodel.setHeaderData(2, Qt.Orientation.Horizontal, "Value")
            self.manager.metaView.setModel(self.metamodel)
            self.manager.metaView.setSelectionBehavior(
                QAbstractItemView.SelectionBehavior.SelectRows
            )
            self.manager.metaView.setSelectionMode(
                QAbstractItemView.SelectionMode.SingleSelection
            )
            self.manager.metaView.hideColumn(0)
            self.manager.metaView.horizontalHeader().setSectionResizeMode(
                2, QHeaderView.ResizeMode.Stretch
            )
            self.manager.metaView.verticalHeader().setVisible(False)
            # Mapper
            self.mapper = QDataWidgetMapper()
            self.mapper.setModel(self.sitemodel)
            self.mapperdelegate = QSqlRelationalDelegate()
            self.mapper.setItemDelegate(self.mapperdelegate)
            self.mapper.addMapping(
                self.manager.xcoord, self.sitemodel.fieldIndex("x_coord")
            )
            self.mapper.addMapping(
                self.manager.ycoord, self.sitemodel.fieldIndex("y_coord")
            )
            self.mapper.addMapping(
                self.manager.siteDesc, self.sitemodel.fieldIndex("description")
            )
            self.mapper.addMapping(self.manager.comboUnit, 1)
            self.mapper.setSubmitPolicy(QDataWidgetMapper.SubmitPolicy.AutoSubmit)

            # connections
            self.siteSelection = self.manager.siteView.selectionModel()
            self.siteSelection.currentRowChanged.connect(self.updateData)
            self.structmodel.dataChanged.connect(self.struct_changed)

            # Track dirty state for apply/reset buttons (after initial load)
            self._update_apply_reset_buttons()

            # update meta coordinate system
            if self.sdb_meta("crs") is None:
                proj4 = self.sdb_meta("proj4")
                if proj4 is None:
                    raise ValueError
                crs = QgsCoordinateReferenceSystem()
                crs.createFromProj4(self.query.value(0))
                self.sdb_meta("crs", crs.authid())
                self.metamodel.setQuery("SELECT * from meta", self.db)

            # qcombobox workaround
            self.manager.comboUnit.currentIndexChanged.connect(
                lambda: self.mapperdelegate.commitData.emit(self.manager.comboUnit)
            )

            self.manager.setWindowTitle(p.name)
            self.manager.siteView.setCurrentIndex(self.sitemodel.index(0, 2))

            self._dirty = False
            self._update_apply_reset_buttons()
            self.dbok = True
            for ac in self.actions:
                ac.setEnabled(True)
            if self.sites_layer is None:
                self.editAction.setEnabled(False)
        except FileNotFoundError:
            self.dbok = False
            self.settings.setValue("sdbname", "")
            for ac in self.actions[2:]:
                ac.setDisabled(True)
            self.bar.pushWarning("SDB Read", self.tr("File not found"))
        except ConnectionError:
            self.dbok = False
            self.settings.setValue("sdbname", "")
            for ac in self.actions[2:]:
                ac.setDisabled(True)
            self.bar.pushWarning("SDB Read", self.tr("Not correct SDB database"))
        except ValueError:
            self.dbok = False
            for ac in self.actions[2:]:
                ac.setDisabled(True)
            self.bar.pushWarning("SDB Read", self.tr("Not CRS or Proj4 in meta table"))

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
        return QCoreApplication.translate("ReadSDB", message)

    def _exec_log(self, query):
        if not query.exec():
            self.log.logMessage(
                "Query error: {} — {}".format(
                    query.lastError().text(), query.lastQuery()
                ),
                "ReadSDB",
                Qgis.Warning,
            )

    def res_path(self, path):
        return os.path.join(self.plugin_dir, path)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None,
    ):
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
            self.iface.addPluginToDatabaseMenu(self.menu, action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ":/plugins/readsdb/icons/icon_sdb.png"
        self.add_action(
            icon_path,
            text=self.tr("Select SDB database..."),
            callback=self.sdb_open,
            add_to_toolbar=False,
            parent=self.iface.mainWindow(),
        )

        icon_path = ":/plugins/readsdb/icons/icon_lyr.png"
        self.add_action(
            icon_path,
            text=self.tr("Create/Update SDB from layer..."),
            callback=self.import_from_layer,
            add_to_toolbar=False,
            parent=self.iface.mainWindow(),
        )

        icon_path = ":/plugins/readsdb/icons/icon_con.png"
        self.connectedAction = self.add_action(
            icon_path,
            text=self.tr("Connect/Disconnect SDB database..."),
            callback=self.sdb_connect,
            add_to_menu=False,
            parent=self.iface.mainWindow(),
        )
        self.connectedAction.setCheckable(True)

        icon_path = ":/plugins/readsdb/icons/icon_man.png"
        self.managerAction = self.add_action(
            icon_path,
            text=self.tr("Open SDB manager"),
            callback=self.pysdb_manager,
            add_to_menu=False,
            parent=self.iface.mainWindow(),
        )
        self.managerAction.setCheckable(True)
        self.manager.visibilityChanged.connect(
            lambda visible: self.managerAction.setChecked(visible)
        )

        icon_path = ":/plugins/readsdb/icons/icon_opt.png"
        self.add_action(
            icon_path,
            text=self.tr("Read SDB options"),
            callback=self.set_options,
            add_to_menu=False,
            parent=self.iface.mainWindow(),
        )

        icon_path = ":/plugins/readsdb/icons/icon_loc.png"
        self.add_action(
            icon_path,
            text=self.tr("Read sites from SDB"),
            callback=self.read_sites,
            add_to_menu=False,
            parent=self.iface.mainWindow(),
        )

        icon_path = ":/plugins/readsdb/icons/icon_str.png"
        self.add_action(
            icon_path,
            text=self.tr("Read structures from SDB"),
            callback=self.read_structures,
            add_to_menu=False,
            parent=self.iface.mainWindow(),
        )

        icon_path = ":/plugins/readsdb/icons/icon_net.png"
        self.add_action(
            icon_path,
            text=self.tr("Plot structures"),
            callback=self.plot_structures,
            add_to_menu=False,
            parent=self.iface.mainWindow(),
        )

        icon_path = ":/plugins/readsdb/icons/icon_edt.png"
        self.editAction = self.add_action(
            icon_path,
            text=self.tr("Edit site"),
            callback=self.edit_site,
            add_to_menu=False,
            parent=self.iface.mainWindow(),
        )
        self.editAction.setCheckable(True)

        # Check database and set actions
        # self.check_db()

        # Connect site edit dialog
        self.manager.siteFind.setPlaceholderText(self.tr("Search pattern"))
        self.manager.siteFind.returnPressed.connect(self.site_find)
        self.manager.pushAddData.clicked.connect(self.manager_add_data)
        self.manager.pushDelData.clicked.connect(self.manager_del_data)
        self.manager.pushAddUnit.clicked.connect(self.manager_add_unit)
        self.manager.pushDelUnit.clicked.connect(self.manager_del_unit)
        self.manager.pushAddPlanar.clicked.connect(self.manager_add_planar)
        self.manager.pushAddLinear.clicked.connect(self.manager_add_linear)
        self.manager.pushDelStructure.clicked.connect(self.manager_del_structure)

        self.manager.pushSelectCRS.clicked.connect(self.manager_set_crs)

        self.manager.buttonBox.button(
            QDialogButtonBox.StandardButton.Apply
        ).clicked.connect(self.apply)
        self.manager.buttonBox.button(
            QDialogButtonBox.StandardButton.Reset
        ).clicked.connect(self.reset)

        xcoord_val = QDoubleValidator(self.manager.xcoord)
        xcoord_val.setDecimals(4)
        ycoord_val = QDoubleValidator(self.manager.ycoord)
        ycoord_val.setDecimals(4)
        self.manager.xcoord.setValidator(xcoord_val)
        self.manager.xcoord.setMaxLength(14)
        self.manager.ycoord.setValidator(ycoord_val)
        self.manager.ycoord.setMaxLength(14)

        # Check database and set actions
        self.dbok = False
        for ac in self.actions[3:]:
            ac.setDisabled(True)
        try:
            p = Path(self.settings.value("sdbname", type=str))
            if not p.is_file():
                self.settings.setValue("sdbname", "")
                raise FileNotFoundError
            conn = sqlite3.connect(str(p))
            conn.row_factory = sqlite3.Row
            conn.execute("pragma encoding='UTF-8'")
            _ = conn.execute(SDB_SELECT + " GROUP BY structdata.id").fetchall()
            res = conn.execute(
                "SELECT value FROM meta WHERE name=?", ("crs",)
            ).fetchall()
            if not res:
                res = conn.execute(
                    "SELECT value FROM meta WHERE name=?", ("proj4",)
                ).fetchall()
                if not res:
                    raise sqlite3.OperationalError
            conn.close()
        except Exception:
            self.actions[2].setDisabled(True)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginDatabaseMenu(self.tr("&Read SDB"), action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        if hasattr(self, "toolbar"):
            del self.toolbar
        # remove dock
        if hasattr(self, "manager"):
            del self.manager
        # close db
        if self.dbok:
            self.db.rollback()
            self.query.prepare("UPDATE meta SET value = ? WHERE name = 'accessed'")
            self.query.addBindValue(datetime.now().strftime("%d.%m.%Y %H:%M"))
            self._exec_log(self.query)
            self.db.commit()
            self.db.close()
        # remove svg path
        readsdb_svg_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "svg"
        )
        svg_paths = QgsSettings().value("svg/searchPathsForSVG")
        if svg_paths:
            if readsdb_svg_path in svg_paths:
                svg_paths.remove(readsdb_svg_path)
                QgsSettings().setValue("svg/searchPathsForSVG", svg_paths)

    def apply(self):
        self.query.prepare("UPDATE meta SET value = ? WHERE name = 'updated'")
        self.query.addBindValue(datetime.now().strftime("%d.%m.%Y %H:%M"))
        self._exec_log(self.query)
        self.db.commit()
        self._dirty = False
        self._update_apply_reset_buttons()
        self.db.transaction()
        self.metamodel.setQuery("SELECT * from meta", self.db)

    def reset(self):
        idx = self.siteSelection.currentIndex()
        self.db.rollback()
        self._dirty = False
        self._update_apply_reset_buttons()
        self.db.transaction()
        self.sitemodel.select()
        self.datamodel.select()
        self.unitmodel.select()
        self.structmodel.select()
        self.tagsmodel.select()
        self.datamodel.relationModel(2).select()
        self.metamodel.setQuery("SELECT * from meta", self.db)
        self.manager.siteView.setCurrentIndex(idx)

    def _set_dirty(self):
        self._dirty = True
        self._update_apply_reset_buttons()

    def _update_apply_reset_buttons(self):
        self.manager.buttonBox.button(QDialogButtonBox.StandardButton.Apply).setEnabled(
            self._dirty
        )
        self.manager.buttonBox.button(QDialogButtonBox.StandardButton.Reset).setEnabled(
            self._dirty
        )

    def struct_changed(self, left, right):
        self.datamodel.relationModel(2).select()

    def sdb_meta(self, name, value=None):
        if value is None:
            self.query.prepare("SELECT value FROM meta WHERE name = ?")
            self.query.addBindValue(name)
            self.query.exec()
            return self.query.value(0) if self.query.first() else None
        else:
            self.query.prepare("SELECT value FROM meta WHERE name = ?")
            self.query.addBindValue(name)
            self.query.exec()
            if self.query.first():
                self.query.prepare("UPDATE meta SET value = ? WHERE name = ?")
                self.query.addBindValue(value)
                self.query.addBindValue(name)
                self._exec_log(self.query)
            else:
                self.query.prepare("INSERT INTO meta (name,value) VALUES (?,?)")
                self.query.addBindValue(name)
                self.query.addBindValue(value)
                self._exec_log(self.query)

    def manager_add_data(self):
        rec = self.datamodel.record()
        row = self.siteSelection.currentIndex().row()
        siteid = self.sitemodel.record(row).value("id")
        rec.setValue(1, siteid)
        rec.setValue(2, 1)
        rec.setValue(3, 0)
        rec.setValue(4, 0)
        if not self.datamodel.insertRecord(-1, rec):
            self.log.logMessage(
                "manager_add_data error: {}".format(self.datamodel.lastError().text()),
                "ReadSDB",
                Qgis.Warning,
            )
        self.datamodel.select()
        self._set_dirty()
        self.manager.dataView.scrollToBottom()

    def manager_del_data(self):
        self.datamodel.deleteRowFromTable(self.manager.dataView.currentIndex().row())
        self.datamodel.select()
        self._set_dirty()

    def manager_add_unit(self):
        self.query.exec("SELECT MAX(pos) FROM units")
        self.query.first()
        pos = self.query.value(0)
        rec = self.unitmodel.record()
        rec.setValue(1, pos + 1)
        rec.setValue(2, "Unit name")
        if not self.unitmodel.insertRecord(-1, rec):
            self.log.logMessage(
                "manager_add_unit error: {}".format(self.unitmodel.lastError().text()),
                "ReadSDB",
                Qgis.Warning,
            )
        self.unitmodel.select()
        self.sitemodel.select()
        self._set_dirty()
        self.manager.unitView.scrollToBottom()

    def manager_del_unit(self):
        row = self.manager.unitView.currentIndex().row()
        rec = self.unitmodel.record(row)
        unitid = rec.value(0)
        self.query.prepare("SELECT name FROM sites WHERE id_units = ?")
        self.query.addBindValue(unitid)
        self.query.exec()
        if self.query.first():
            self.bar.pushWarning(
                "SDB Read",
                self.tr("Current unit is in use e.g. site {}").format(
                    self.query.value(0)
                ),
            )
        else:
            self.unitmodel.deleteRowFromTable(row)
            self.unitmodel.select()
            self.sitemodel.select()
            self._set_dirty()

    def manager_add_planar(self):
        self.query.exec("SELECT MAX(pos) FROM structype")
        self.query.first()
        pos = self.query.value(0)
        rec = self.structmodel.record()
        rec.setValue(1, pos + 1)
        rec.setValue(2, "S")
        rec.setValue(4, 35)
        rec.setValue(5, 13)
        rec.setValue(6, 1)
        if not self.structmodel.insertRecord(-1, rec):
            self.log.logMessage(
                "manager_add_planar error: {}".format(
                    self.structmodel.lastError().text()
                ),
                "ReadSDB",
                Qgis.Warning,
            )
        self.structmodel.select()
        self.datamodel.relationModel(2).select()
        self.datamodel.select()
        self._set_dirty()
        self.manager.structuresView.scrollToBottom()

    def manager_add_linear(self):
        self.query.exec("SELECT MAX(pos) FROM structype")
        self.query.first()
        pos = self.query.value(0)
        rec = self.structmodel.record()
        rec.setValue(1, pos + 1)
        rec.setValue(2, "L")
        rec.setValue(4, 78)
        rec.setValue(5, 13)
        rec.setValue(6, 0)
        if not self.structmodel.insertRecord(-1, rec):
            self.log.logMessage(
                "manager_add_linear error: {}".format(
                    self.structmodel.lastError().text()
                ),
                "ReadSDB",
                Qgis.Warning,
            )
        self.structmodel.select()
        self.datamodel.select()
        self._set_dirty()
        self.manager.structuresView.scrollToBottom()

    def manager_del_structure(self):
        row = self.manager.structuresView.currentIndex().row()
        rec = self.structmodel.record(row)
        strucid = rec.value(0)
        self.query.prepare(
            "SELECT sites.name as name FROM structdata INNER JOIN sites ON structdata.id_sites=sites.id INNER JOIN structype ON structype.id = structdata.id_structype INNER JOIN units ON units.id = sites.id_units  WHERE structdata.id_structype = ? LIMIT 1"
        )
        self.query.addBindValue(strucid)
        self.query.exec()
        if self.query.first():
            self.bar.pushWarning(
                "SDB Read",
                self.tr("Current structure is in use e.g. site {}").format(
                    self.query.value(0)
                ),
            )
        else:
            self.structmodel.deleteRowFromTable(row)
            self.structmodel.select()
            self.datamodel.relationModel(2).select()
            self.datamodel.select()
            self._set_dirty()

    def manager_set_crs(self):
        crs_dlg = QgsProjectionSelectionDialog(self.manager)
        if crs_dlg.exec():
            self.sdb_meta("crs", crs_dlg.crs().authid())
            self.metamodel.setQuery("SELECT * from meta", self.db)
            self._set_dirty()

    def updateData(self, selected, deselected):
        # Detect site edits before switching away
        if hasattr(self, "_site_original_vals"):
            if (
                self._site_original_vals["xcoord"] != self.manager.xcoord.text()
                or self._site_original_vals["ycoord"] != self.manager.ycoord.text()
                or self._site_original_vals["siteDesc"]
                != self.manager.siteDesc.toPlainText()
                or self._site_original_vals["comboUnit"]
                != self.manager.comboUnit.currentText()
            ):
                self._set_dirty()
        self.mapper.setCurrentModelIndex(selected)
        self._site_original_vals = {
            "xcoord": self.manager.xcoord.text(),
            "ycoord": self.manager.ycoord.text(),
            "siteDesc": self.manager.siteDesc.toPlainText(),
            "comboUnit": self.manager.comboUnit.currentText(),
        }
        self.datamodel.setFilter(
            "structdata.id_sites={}".format(
                self.sitemodel.record(selected.row()).value("id")
            )
        )
        self.datamodel.select()

    def site_find(self):
        row = self.manager.siteView.currentIndex().row()
        if row < self.sitemodel.rowCount() - 1:
            start = self.sitemodel.index(row + 1, 2)
        else:
            start = self.sitemodel.index(0, 2)
        matches = self.sitemodel.match(
            start,
            Qt.ItemDataRole.DisplayRole,
            self.manager.siteFind.text(),
            2,
            Qt.MatchFlag.MatchContains,
        )
        if matches:
            index = matches[0]
            self.manager.siteView.setCurrentIndex(index)
        else:
            start = self.sitemodel.index(0, 2)
            matches = self.sitemodel.match(
                start,
                Qt.ItemDataRole.DisplayRole,
                self.manager.siteFind.text(),
                2,
                Qt.MatchFlag.MatchContains,
            )
            if matches:
                index = matches[0]
                self.manager.siteView.setCurrentIndex(index)

    def check_site_layer(self):
        if self.sites_layer not in QgsProject.instance().mapLayers().values():
            self.editAction.setChecked(False)
            self.editAction.setEnabled(False)

    def calc_gc(self, point=None):
        """Calculate Grid convergence for project CRS"""
        crsSrc = QgsProject.instance().crs()
        crsDst = QgsCoordinateReferenceSystem.fromEpsgId(4326)
        xform = QgsCoordinateTransform(crsSrc, crsDst, QgsProject.instance())

        if point is None:
            point = self.iface.mapCanvas().extent().center()
        point_ll = xform.transform(point, QgsCoordinateTransform.ForwardTransform)

        if point_ll.y() < 89.9:
            point_ll_shift = QgsPointXY(point_ll.x(), point_ll.y() + 0.01)
            point_north = xform.transform(
                point_ll_shift, QgsCoordinateTransform.ReverseTransform
            )
            gc = point.azimuth(point_north)
        else:
            point_ll_shift = QgsPointXY(point_ll.x(), point_ll.y() - 0.01)
            point_north = xform.transform(
                point_ll_shift, QgsCoordinateTransform.ReverseTransform
            )
            gc = point_north.azimuth(point)
        return gc

    def calc_md(self, point=None, time=date.today()):
        """Calculate magnetic declination uising Christopher Weiss geomag library.

        Adapted from the geomagc software and World Magnetic Model of the NOAA
        Satellite and Information Service, National Geophysical Data Center
        http://www.ngdc.noaa.gov/geomag/WMM/DoDWMM.shtml
        """
        crsSrc = QgsProject.instance().crs()
        crsDst = QgsCoordinateReferenceSystem.fromEpsgId(4326)
        xform = QgsCoordinateTransform(crsSrc, crsDst, QgsProject.instance())

        if point is None:
            point = self.iface.mapCanvas().extent().center()
        point_ll = xform.transform(point, QgsCoordinateTransform.ForwardTransform)

        mag = GM.GeoMag(point_ll.y(), point_ll.x(), time=time)
        return mag.dec

    def sanitize(self, text):
        rtext = ""
        if text is not None:
            rtext = str(text).replace("\r\n", " ").replace("\n", " ")
        return rtext

    def sdb_open(self):
        # self.open_dlg.show()
        # Populate info
        self.open_dlg.sdbinfo(self.settings.value("sdbname", type=str))
        # Run the dialog event loop
        if self.open_dlg.exec():
            self.connectedAction.setChecked(False)
            self.connectedAction.setIcon(QIcon(":/plugins/readsdb/icons/icon_con.png"))
            self.dbok = False
            self.actions[2].setDisabled(False)
            for ac in self.actions[3:]:
                ac.setDisabled(True)

    def sdb_connect(self):
        if self.connectedAction.isChecked():
            self.check_db()
            self.manager.siteView.setCurrentIndex(self.sitemodel.index(0, 2))
            self.connectedAction.setIcon(
                QIcon(":/plugins/readsdb/icons/icon_discon.png")
            )
        else:
            if self.db.isOpen():
                self.db.close()
            if self.managerAction.isChecked():
                self.managerAction.setChecked(False)
                self.iface.removeDockWidget(self.manager)
            self.editSiteTool = None
            self.editAction.setChecked(False)
            self._dirty = False
            self._update_apply_reset_buttons()
            self.dbok = False
            for ac in self.actions[3:]:
                ac.setDisabled(True)
            self.connectedAction.setIcon(QIcon(":/plugins/readsdb/icons/icon_con.png"))

    def pysdb_manager(self):
        """Add PySDB manager"""
        if self.managerAction.isChecked():
            self.iface.addDockWidget(
                Qt.DockWidgetArea.RightDockWidgetArea, self.manager
            )
        else:
            self.iface.removeDockWidget(self.manager)

    def set_options(self):
        """Select database and set plugin options"""
        # show the dialog
        self.options_dlg.show()
        # populate dialog
        self.options_dlg.angle_gc.setText(self.settings.value("angle_gc", type=str))
        self.options_dlg.angle_md.setText(self.settings.value("angle_md", type=str))
        self.options_dlg.offset.setText(self.settings.value("offset", type=str))
        self.options_dlg.linmulti.setText(self.settings.value("linmulti", type=str))
        self.options_dlg.corr_gc_auto.setChecked(
            self.settings.value("auto_gc", type=bool)
        )
        self.options_dlg.corr_md_auto.setChecked(
            self.settings.value("auto_md", type=bool)
        )
        # set magnetic declination calendar
        try:
            md_time = datetime.strptime(
                self.sdb_meta("measured"), "%d.%m.%Y %H:%M"
            ).date()
        except TypeError:
            md_time = datetime.strptime(
                self.sdb_meta("created"), "%d.%m.%Y %H:%M"
            ).date()
        self.options_dlg.dateEdit.setDate(
            QDate(md_time.year, md_time.month, md_time.day)
        )
        # Run the dialog event loop
        self.options_dlg.exec()

    def get_add_unit(self, unitname, query=None):
        if query is None:
            query = self.query
        query.prepare("SELECT id FROM units WHERE name = ?")
        query.addBindValue(unitname)
        query.exec()
        if query.first():
            idunit = query.value(0)
        else:
            query.exec("SELECT MAX(pos) FROM units")
            query.first()
            pos = query.value(0)
            query.prepare("INSERT INTO units (pos,name) VALUES (?,?)")
            query.addBindValue(pos + 1)
            query.addBindValue(unitname)
            self._exec_log(query)
            idunit = query.lastInsertId()
        return idunit

    def add_update_site(self, idunit, name, x, y, desc, update=False, query=None):
        if query is None:
            query = self.query
        if update:
            query.prepare("SELECT id FROM sites WHERE name = ?")
            query.addBindValue(name)
            query.exec()
            if query.first():
                query.prepare(
                    "UPDATE sites SET id_units = ?, x_coord = ?, y_coord = ?, description = ? WHERE name = ?"
                )
                query.addBindValue(idunit)
                query.addBindValue(x)
                query.addBindValue(y)
                query.addBindValue(desc)
                query.addBindValue(name)
                self._exec_log(query)
        else:
            query.prepare(
                "INSERT INTO sites (id_units,name,x_coord,y_coord,description) VALUES (?,?,?,?,?)"
            )
            query.addBindValue(idunit)
            query.addBindValue(name)
            query.addBindValue(x)
            query.addBindValue(y)
            query.addBindValue(desc)
            self._exec_log(query)

    def import_from_layer(self):
        layers = QgsProject.instance().mapLayers().values()
        if len(layers) > 0:
            dlg = ReadSDBImportLayer(self)
            if not self.dbok:
                dlg.radioButtonNew.setChecked(True)
                dlg.radioButtonNew.setEnabled(False)
                dlg.radioButtonUpdate.setChecked(False)
                dlg.radioButtonUpdate.setEnabled(False)
            else:
                dlg.radioButtonNew.setChecked(False)
                dlg.radioButtonNew.setEnabled(True)
                dlg.radioButtonUpdate.setChecked(True)
                dlg.radioButtonUpdate.setEnabled(True)
            result = dlg.exec()
            if result:
                if dlg.radioButtonNew.isChecked():
                    fname, _ = QFileDialog.getSaveFileName(
                        None, "New database", ".", "SDB database (*.sdb)"
                    )
                    if fname:
                        QgsApplication.instance().setOverrideCursor(
                            QCursor(Qt.CursorShape.WaitCursor)
                        )

                        p = Path(fname)
                        if not p.suffix:
                            p = p.with_suffix(".sdb")
                        # close if open
                        if hasattr(self, "db") and self.db.isValid():
                            self.reset()
                            self.db.close()
                            self.editSiteTool = None
                            self.editAction.setChecked(False)
                        db = QSqlDatabase.addDatabase("QSQLITE", "readsdb_import")
                        db.setDatabaseName(str(p))
                        if not db.open():
                            QMessageBox.critical(
                                None,
                                "Cannot open database",
                                "Unable to establish a database connection.\n"
                                "This example needs SQLite support. Please read the Qt SQL "
                                "driver documentation for information how to build it.\n\n"
                                "Click Cancel to exit.",
                                QMessageBox.Cancel,
                            )
                            restore_cursor()
                            return
                        # process layer
                        layer = dlg.layerCombo.currentLayer()
                        site_field = dlg.siteCombo.currentField()
                        unit_field = dlg.unitCombo.currentField()
                        desc_field = dlg.descCombo.currentField()
                        query = QSqlQuery()
                        for sql in SCHEMA_NEW.splitlines():
                            query.exec(sql)
                        # Insert metadata
                        meta_values = [
                            ("version", SDB_VERSION),
                            ("crs", layer.crs().authid()),
                            ("created", datetime.now().strftime("%d.%m.%Y %H:%M")),
                            ("updated", datetime.now().strftime("%d.%m.%Y %H:%M")),
                            ("accessed", datetime.now().strftime("%d.%m.%Y %H:%M")),
                        ]
                        for mk, mv in meta_values:
                            query.prepare("INSERT INTO meta (name,value) VALUES (?,?)")
                            query.addBindValue(mk)
                            query.addBindValue(mv)
                            if not query.exec():
                                self.log.logMessage(
                                    "Failed to insert meta {}: {}".format(
                                        mk, query.lastError().text()
                                    ),
                                    "ReadSDB",
                                    Qgis.Warning,
                                )
                        # Insert sites and units
                        features = layer.getFeatures()
                        for feature in features:
                            pt = feature.geometry().asPoint()
                            idunit = (
                                1
                                if unit_field == ""
                                else self.get_add_unit(feature[unit_field], query=query)
                            )
                            desc = (
                                ""
                                if desc_field == ""
                                else self.sanitize(str(feature[desc_field]))
                            )
                            self.add_update_site(
                                idunit,
                                feature[site_field],
                                pt.x(),
                                pt.y(),
                                desc,
                                update=False,
                                query=query,
                            )
                        db.commit()
                        db.close()
                        QSqlDatabase.removeDatabase("readsdb_import")
                        self.settings.setValue("sdbname", str(p))
                        self.check_db()
                        self.editSiteTool = None
                        self.editAction.setChecked(False)
                        self.dbok = False
                        for ac in self.actions[3:]:
                            ac.setDisabled(True)
                        self.connectedAction.setChecked(False)
                        self.connectedAction.setIcon(
                            QIcon(":/plugins/readsdb/icons/icon_con.png")
                        )
                        self.bar.pushSuccess(
                            "SDB Read", self.tr("Database succesfully created")
                        )
                        restore_cursor()
                elif dlg.radioButtonUpdate.isChecked():
                    QgsApplication.instance().setOverrideCursor(
                        QCursor(Qt.CursorShape.WaitCursor)
                    )

                    layer = dlg.layerCombo.currentLayer()
                    site_field = dlg.siteCombo.currentField()
                    unit_field = dlg.unitCombo.currentField()
                    desc_field = dlg.descCombo.currentField()
                    features = layer.getFeatures()
                    for feature in features:
                        pt = feature.geometry().asPoint()
                        idunit = (
                            1
                            if unit_field == ""
                            else self.get_add_unit(feature[unit_field])
                        )
                        desc = (
                            ""
                            if desc_field == ""
                            else self.sanitize(str(feature[desc_field]))
                        )
                        self.add_update_site(
                            idunit,
                            feature[site_field],
                            pt.x(),
                            pt.y(),
                            desc,
                            update=True,
                        )
                    self.sdb_meta("crs", layer.crs().authid())
                    self.apply()
                    self.check_db()
                    self.bar.pushSuccess(
                        "SDB Read", self.tr("Database succesfully updated")
                    )
                    restore_cursor()
                else:
                    pass
        else:
            self.bar.pushWarning("SDB Import/Update", self.tr("No layer in project."))

    def create_layer(self, name, fields):
        """Create temporary point layer"""
        crs = QgsCoordinateReferenceSystem()
        crs.createFromUserInput(self.sdb_meta("crs"))
        lyr_fields = QgsFields()
        for key in fields:
            lyr_fields.append(QgsField(key, fields[key]))
        layer = QgsMemoryProviderUtils.createMemoryLayer(
            name, lyr_fields, QgsWkbTypes.Point, crs
        )
        return layer

    def read_sites(self):
        """Read sites from SDB database"""
        if self.sites_layer not in QgsProject.instance().mapLayers().values():
            QgsApplication.instance().setOverrideCursor(
                QCursor(Qt.CursorShape.WaitCursor)
            )

            layer = self.create_layer("Sites", site_fields)
            provider = layer.dataProvider()
            layer.startEditing()
            self.query.exec(
                "SELECT sites.id as id, sites.name as name, units.name as unit, sites.x_coord as x, sites.y_coord as y, sites.description as description FROM sites INNER JOIN units ON units.id = sites.id_units ORDER BY sites.id"
            )
            while self.query.next():
                feature = QgsFeature()
                feature.setGeometry(
                    QgsGeometry.fromPointXY(
                        QgsPointXY(self.query.value("x"), self.query.value("y"))
                    )
                )
                feature.setAttributes(
                    [
                        self.query.value("id"),
                        self.query.value("name"),
                        self.query.value("unit"),
                        self.sanitize(self.query.value("description")),
                    ]
                )
                provider.addFeatures([feature])

            layer.commitChanges()
            # Style layer
            layer.loadNamedStyle(self.res_path("styles/sites.qml"))
            layer.triggerRepaint()
            # add to project
            QgsProject.instance().addMapLayer(layer)
            # store pointer
            self.sites_layer = layer
            # enable site edit action
            self.editAction.setEnabled(True)
            restore_cursor()

            if layer.featureCount() > 0:
                self.bar.pushSuccess(
                    "SDB Read",
                    "{} ".format(layer.featureCount())
                    + self.tr("sites read successfully"),
                )
            else:
                self.bar.pushWarning(
                    "SDB Read", self.tr("There are no sites in database")
                )
        else:
            self.bar.pushWarning("SDB Read", self.tr("Sites layer already exists."))

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
        self.query.exec("SELECT structure FROM structype")
        while self.query.next():
            self.structures_dlg.comboStructure.addItem(self.query.value(0))
        self.structures_dlg.comboUnit.clear()
        self.structures_dlg.comboUnit.addItem("Any")
        self.query.exec("SELECT name FROM units")
        while self.query.next():
            self.structures_dlg.comboUnit.addItem(self.query.value(0))
        self.structures_dlg.checkAverage.setChecked(False)
        self.structures_dlg.checkSelected.setEnabled(selected_enable)
        self.structures_dlg.checkSelected.setChecked(selected_enable)
        self.structures_dlg.listTags.clear()
        self.query.exec("SELECT name FROM tags")
        while self.query.next():
            self.structures_dlg.listTags.addItem(self.query.value(0))
        # Run the dialog event loop
        result = self.structures_dlg.exec()
        # See if OK was pressed
        if result:
            QgsApplication.instance().setOverrideCursor(
                QCursor(Qt.CursorShape.WaitCursor)
            )

            layer_name = str(self.structures_dlg.comboStructure.currentText())
            if self.structures_dlg.checkAverage.isChecked():
                layer_name += " averaged"

            layer = self.create_layer(layer_name, structure_fields)
            provider = layer.dataProvider()
            layer.startEditing()

            # set db->project transform
            crsSrc = layer.crs()
            crsDst = QgsProject.instance().crs()
            xform = QgsCoordinateTransform(crsSrc, crsDst, QgsProject.instance())
            # declination calculated for creation date of sdb database
            try:
                md_time = datetime.strptime(
                    self.sdb_meta("measured"), "%d.%m.%Y %H:%M"
                ).date()
            except (ValueError, TypeError):
                md_time = datetime.strptime(
                    self.sdb_meta("created"), "%d.%m.%Y %H:%M"
                ).date()

            struct = str(self.structures_dlg.comboStructure.currentText())
            self.query.prepare("SELECT planar FROM structype WHERE structure = ?")
            self.query.addBindValue(struct)
            self.query.exec()
            self.query.first()
            layer._is_planar = self.query.value(0)
            unit = str(self.structures_dlg.comboUnit.currentText())
            if unit == "Any":
                unit = None
            tags = [
                item.text() for item in self.structures_dlg.listTags.selectedItems()
            ]

            # which sites
            if selected_enable and self.structures_dlg.checkSelected.isChecked():
                sites = [f["name"] for f in self.sites_layer.selectedFeatures()]
            else:
                sites = []
                sql, params = sdb_make_select(structs=struct, units=unit, tags=tags)
                self.query.prepare(sql)
                for p in params:
                    self.query.addBindValue(p)
                self.query.exec()
                while self.query.next():
                    sites.append(self.query.value("name"))
                sites = sorted(list(set(sites)))
            # get scale for label offset (use linear multiplier for linear features)
            off_coef = (
                1.0 if layer._is_planar else self.settings.value("linmulti", type=float)
            )

            # create features from data rows
            for site in sites:
                # do site select to get data
                sql, params = sdb_make_select(
                    sites=site, structs=struct, units=unit, tags=tags
                )
                self.query.prepare(sql)
                for p in params:
                    self.query.addBindValue(p)
                self.query.exec()
                # average?
                dt = []
                if self.structures_dlg.checkAverage.isChecked():
                    if self.query.first():
                        azi = [self.query.value("azimuth")]
                        inc = [self.query.value("inclination")]
                        rec = {
                            key: self.query.value(key)
                            for key in [
                                "name",
                                "x",
                                "y",
                                "unit",
                                "structure",
                                "planar",
                                "description",
                                "tags",
                            ]
                        }
                        while self.query.next():
                            azi.append(self.query.value("azimuth"))
                            inc.append(self.query.value("inclination"))
                        if layer._is_planar:
                            g = folset.from_array(azi, inc)
                            dd = g.ortensor().eigenfols()[0].geo
                        else:
                            g = linset.from_array(azi, inc)
                            dd = g.ortensor().eigenlins()[0].geo
                        rec["azimuth"] = float(dd[0])
                        rec["inclination"] = float(dd[1])
                        rec["description"] = "Averaged from {} data".format(len(g))
                        rec["tags"] = None
                        dt = [rec]
                else:
                    while self.query.next():
                        rec = {
                            key: self.query.value(key)
                            for key in [
                                "name",
                                "x",
                                "y",
                                "unit",
                                "azimuth",
                                "inclination",
                                "structure",
                                "planar",
                                "description",
                                "tags",
                            ]
                        }
                        dt.append(rec)
                # add features
                for rec in dt:
                    feature = QgsFeature()
                    point = QgsPointXY(rec["x"], rec["y"])
                    feature.setGeometry(QgsGeometry.fromPointXY(point))
                    # do possible azimuth corrections in canvas crs
                    point_canvas = xform.transform(
                        point, QgsCoordinateTransform.ForwardTransform
                    )
                    delta = 0
                    delta += (
                        self.calc_gc(point=point_canvas)
                        if self.settings.value("auto_gc", type=bool)
                        else self.settings.value("angle_gc", type=float)
                    )
                    delta += (
                        self.calc_md(point=point_canvas, time=md_time)
                        if self.settings.value("auto_md", type=bool)
                        else self.settings.value("angle_md", type=float)
                    )
                    rotation = rec["azimuth"] + delta
                    # calculate label offset
                    offx = (
                        off_coef
                        * self.settings.value("offset", type=float)
                        * sin(rotation * pi / 180.0)
                    )
                    offy = (
                        -off_coef
                        * self.settings.value("offset", type=float)
                        * cos(rotation * pi / 180.0)
                    )
                    atts = [
                        rec["name"],
                        rec["unit"],
                        rec["azimuth"],
                        rec["inclination"],
                        rec["structure"],
                        rec["tags"],
                        self.sanitize(rec["description"]),
                        rec["planar"],
                        rotation,
                        int(round(rec["inclination"])),
                        "{},{}".format(offx, offy),
                    ]
                    feature.setAttributes(atts)
                    provider.addFeatures([feature])

            layer.commitChanges()
            if layer.featureCount() > 0:
                # Style layer
                if layer._is_planar:
                    layer.loadNamedStyle(self.res_path("styles/planar.qml"))
                else:
                    layer.loadNamedStyle(self.res_path("styles/linear.qml"))
                layer.triggerRepaint()
                # add to project
                QgsProject.instance().addMapLayer(layer)
                self.bar.pushSuccess(
                    "SDB Read",
                    "{} ".format(layer.featureCount())
                    + self.tr("structures read successfully"),
                )
            else:
                self.bar.pushSuccess(
                    "SDB Read",
                    self.tr("No structures found. Choose different criteria"),
                )

            restore_cursor()

    def plot_structures(self):
        """Select database and set plugin options"""
        layers = self.iface.layerTreeView().selectedLayers()
        self.plot_dlg.tabWidget.clear()
        self.plot_dlg.data_layers = []
        idx = 0
        for layer in layers:
            if hasattr(layer, "_is_planar"):
                self.plot_dlg.data_layers.append((idx, layer))
                if layer._is_planar:
                    w = uic.loadUi(
                        os.path.join(os.path.dirname(__file__), "ui/widget_planar.ui")
                    )
                else:
                    w = uic.loadUi(
                        os.path.join(os.path.dirname(__file__), "ui/widget_linear.ui")
                    )
                self.plot_dlg.tabWidget.addTab(w, layer.name())
                idx += 1
        if idx > 0:
            # show the dialog
            self.plot_dlg.show()
            # prepare stereo net
            self.plot_dlg.plotnet()
            # Run the dialog event loop
            self.plot_dlg.exec()

    def edit_site(self):
        """Select database and set plugin options"""
        if self.sites_layer not in QgsProject.instance().mapLayers().values():
            self.bar.pushSuccess(
                "SDB Read", self.tr("You have to read localities before use this tool.")
            )
            self.editAction.setChecked(False)
        else:
            if self.editAction.isChecked():
                self.editSiteTool = QgsMapToolIdentifyFeature(self.iface.mapCanvas())
                self.editSiteTool.setLayer(self.sites_layer)
                self.iface.mapCanvas().setMapTool(self.editSiteTool)
                self.editSiteTool.featureIdentified.connect(self.on_site_edit)
            else:
                self.editSiteTool = None

    def on_site_edit(self, feature):
        matches = self.sitemodel.match(
            self.sitemodel.index(0, 2),
            Qt.ItemDataRole.DisplayRole,
            feature["name"],
            2,
            Qt.MatchFlag.MatchExactly,
        )
        if matches:
            index = matches[0]
            self.manager.siteView.setCurrentIndex(index)
