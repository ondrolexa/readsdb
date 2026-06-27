#! python3  # noqa E265

"""
    Usage from the repo root folder:

    .. code-block:: bash

        # for whole tests
        python -m unittest tests.qgis.test_plg_preferences
        # for specific test
        python -m unittest tests.qgis.test_plg_preferences.TestPlgPreferences.test_plg_preferences_structure
"""

# standard library
import os
from unittest.mock import patch

from qgis.testing import unittest

# project
from readsdb.__about__ import __version__
from readsdb.toolbelt.preferences import (
    PREFIX_ENV_VARIABLE,
    PlgOptionsManager,
    PlgSettingsStructure,
)

# ############################################################################
# ########## Classes #############
# ################################


class TestPlgPreferences(unittest.TestCase):
    def test_plg_preferences_structure(self):
        """Test settings types and default values."""
        settings = PlgSettingsStructure()

        # global
        self.assertTrue(hasattr(settings, "debug_mode"))
        self.assertIsInstance(settings.debug_mode, bool)
        self.assertEqual(settings.debug_mode, False)

        self.assertTrue(hasattr(settings, "version"))
        self.assertIsInstance(settings.version, str)
        self.assertEqual(settings.version, __version__)

    def test_bool_env_variable(self):
        """Test settings with environment value."""
        manager = PlgOptionsManager()
        with patch.dict(
            os.environ, {f"{PREFIX_ENV_VARIABLE}DEBUG_MODE": "true"}, clear=True
        ):
            settings = manager.get_plg_settings()
            self.assertEqual(settings.debug_mode, True)

        with patch.dict(
            os.environ, {f"{PREFIX_ENV_VARIABLE}DEBUG_MODE": "false"}, clear=True
        ):
            settings = manager.get_plg_settings()
            self.assertEqual(settings.debug_mode, False)

        with patch.dict(
            os.environ, {f"{PREFIX_ENV_VARIABLE}DEBUG_MODE": "on"}, clear=True
        ):
            settings = manager.get_plg_settings()
            self.assertEqual(settings.debug_mode, True)

        with patch.dict(
            os.environ, {f"{PREFIX_ENV_VARIABLE}DEBUG_MODE": "off"}, clear=True
        ):
            settings = manager.get_plg_settings()
            self.assertEqual(settings.debug_mode, False)

        with patch.dict(
            os.environ, {f"{PREFIX_ENV_VARIABLE}DEBUG_MODE": "1"}, clear=True
        ):
            settings = manager.get_plg_settings()
            self.assertEqual(settings.debug_mode, True)

        with patch.dict(
            os.environ, {f"{PREFIX_ENV_VARIABLE}DEBUG_MODE": "0"}, clear=True
        ):
            settings = manager.get_plg_settings()
            self.assertEqual(settings.debug_mode, False)

        with patch.dict(
            os.environ,
            {f"{PREFIX_ENV_VARIABLE}DEBUG_MODE": "invalid_value"},
            clear=True,
        ):
            settings = manager.get_plg_settings()
            self.assertEqual(settings.debug_mode, False)


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
