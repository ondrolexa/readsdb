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

from qgis.PyQt import QtWidgets, uic
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
