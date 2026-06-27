#! python3  # noqa: E265

# ----------------------------------------------------------
# ReadSDB QGIS Plugin
# Copyright (C) 2026 Ondrej Lexa
# ----------------------------------------------------------
# Licensed under the terms of MIT
# ----------------------------------------------------------


def classFactory(iface):
    """Load the plugin class.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    from .plugin_main import ReadSDBPlugin

    return ReadSDBPlugin(iface)
