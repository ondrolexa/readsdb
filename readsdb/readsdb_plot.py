# -*- coding: utf-8 -*-

# ----------------------------------------------------------
# ReadSDB QGIS Plugin
# Copyright (C) 2026 Ondrej Lexa
# ----------------------------------------------------------
# Licensed under the terms of MIT
# ----------------------------------------------------------

import os

from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

import matplotlib

matplotlib.use("QtAgg")
from apsg import StereoNet, apsg_conf, fol, folset, lin, linset

apsg_conf.dpi = 100


FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "ui/readsdb_plot.ui")
)


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None):
        self.net = StereoNet()
        self.net.init_figure()
        super(MyMplCanvas, self).__init__(self.net.fig)
        self.setParent(parent)
        super(MyMplCanvas, self).setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        super(MyMplCanvas, self).updateGeometry()


class ReadSDBPlotDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, readsdb, parent=None):
        """Constructor."""
        super(ReadSDBPlotDialog, self).__init__(
            parent, Qt.WindowType.WindowStaysOnTopHint
        )
        self.setupUi(self)
        self.pushApply.clicked.connect(self.plotnet)
        self.data_layers = []
        self.canvas = None
        self.toolbar = None
        self.net = None

    def _init_canvas(self):
        if self.canvas is not None:
            return
        self.mplLayout.takeAt(0)
        self.canvas = MyMplCanvas(self)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.mplLayout.addWidget(self.canvas)
        self.mplLayout.addWidget(self.toolbar)
        self.net = self.canvas.net

    def opt(self, index, type_, name):
        return self.tabWidget.widget(index).findChild(type_, name)

    def plotnet(self):
        self._init_canvas()
        self.net.clear()
        self.net._kwargs["overlay"] = self.checkGrid.isChecked()
        for idx, layer in self.data_layers[::-1]:
            if layer.selectedFeatureCount():
                features = layer.getSelectedFeatures()
            else:
                features = layer.getFeatures()
            if layer._is_planar:
                g = folset(
                    [fol(f.attribute("azi"), f.attribute("inc")) for f in features],
                    layer.name(),
                )
            else:
                g = linset(
                    [lin(f.attribute("azi"), f.attribute("inc")) for f in features],
                    layer.name(),
                )
            label = repr(g) if self.checkLabels.isChecked() else ""
            if self.opt(idx, QtWidgets.QCheckBox, "checkContours").isChecked():
                nlevels = self.opt(idx, QtWidgets.QSpinBox, "spinLevels").value()
                n_max = self.opt(idx, QtWidgets.QSpinBox, "spinResolution").value() * 2
                self.net.contour(
                    g,
                    levels=nlevels,
                    n_max=n_max,
                    colorbar=self.checkLabels.isChecked(),
                    clines=self.opt(
                        idx, QtWidgets.QCheckBox, "checkContourLines"
                    ).isChecked(),
                )
            markersize = self.opt(idx, QtWidgets.QSpinBox, "spinSize").value()
            marker = self.opt(idx, QtWidgets.QComboBox, "comboStyle").currentText()
            if layer._is_planar:
                if self.opt(idx, QtWidgets.QCheckBox, "checkShowData").isChecked():
                    if self.opt(idx, QtWidgets.QCheckBox, "checkAsPoles").isChecked():
                        self.net.pole(g, marker=marker, ms=markersize, label=label)
                    else:
                        self.net.great_circle(g, label=label)
            else:
                if self.opt(idx, QtWidgets.QCheckBox, "checkShowData").isChecked():
                    self.net.line(g, marker=marker, ms=markersize, label=label)
            if self.opt(idx, QtWidgets.QCheckBox, "checkEigPlanes").isChecked():
                self.net.great_circle(
                    *g.ortensor().eigenfols(),
                    label="E-fols" if self.checkLabels.isChecked() else ""
                )
            if self.opt(idx, QtWidgets.QCheckBox, "checkEigLines").isChecked():
                self.net.line(
                    *g.ortensor().eigenlins(),
                    marker="s",
                    ms=8,
                    label="E-lins" if self.checkLabels.isChecked() else ""
                )

        self.net.fig.clear()
        self.net._render()
        self.canvas.draw()
