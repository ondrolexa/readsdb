# -*- coding: utf-8 -*-

# ----------------------------------------------------------
# ReadSDB QGIS Plugin
# Copyright (C) 2026 Ondrej Lexa
# ----------------------------------------------------------
# Licensed under the terms of MIT
# ----------------------------------------------------------

import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import Qt

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "ui/readsdb_structures.ui")
)


class ReadSDBStructuresDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, readsdb, parent=None):
        """Constructor."""
        super(ReadSDBStructuresDialog, self).__init__(
            parent, Qt.WindowType.WindowStaysOnTopHint
        )
        self.setupUi(self)
