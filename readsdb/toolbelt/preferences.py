#! python3  # noqa: E265

"""Plugin settings."""

# standard
from dataclasses import asdict, dataclass, fields
from typing import Any

# PyQGIS
from qgis.core import Qgis, QgsSettings

# package
import readsdb.toolbelt.log_handler as log_hdlr
from readsdb.__about__ import __title__, __version__
from readsdb.toolbelt.env_var_parser import EnvVarParser

# -- GLOBALS --
PREFIX_ENV_VARIABLE = "QGIS_READSDB_"

# ############################################################################
# ########## Classes ###############
# ##################################


@dataclass
class PlgEnvVariableSettings:
    """Plugin settings from environnement variable"""

    def env_variable_used(self, attribute: str, default_from_name: bool = True) -> str:
        """Get environnement variable used for environnement variable settings

        :param attribute: attribute to check
        :type attribute: str
        :param default_from_name: define default environnement value from attribute name
            PREFIX_ENV_VARIABLE_<upper case attribute>
        :type default_from_name: bool
        :return: environnement variable used
        :rtype: str
        """
        settings_env_variable: dict[str, Any] = asdict(self)
        env_variable = settings_env_variable.get(attribute, "")
        if not env_variable and default_from_name:
            env_variable: str = f"{PREFIX_ENV_VARIABLE}{attribute}".upper()
        return env_variable


@dataclass
class PlgSettingsStructure:
    """Plugin settings structure and defaults values."""

    # global
    debug_mode: bool = False
    version: str = __version__


class PlgOptionsManager:
    @staticmethod
    def get_plg_settings() -> PlgSettingsStructure:
        """Load and return plugin settings as a dictionary. \
        Useful to get user preferences across plugin logic.

        :return: plugin settings
        :rtype: PlgSettingsStructure
        """
        # get dataclass fields definition
        settings_fields = fields(PlgSettingsStructure)
        env_variable_settings = PlgEnvVariableSettings()

        # retrieve settings from QGIS/Qt
        settings = QgsSettings()
        settings.beginGroup(__title__)

        # map settings values to preferences object
        li_settings_values = []
        for i in settings_fields:
            try:
                value = settings.value(key=i.name, defaultValue=i.default, type=i.type)
                # If environnement variable used, get value from environnement variable
                env_variable = env_variable_settings.env_variable_used(i.name)
                if env_variable:
                    value = EnvVarParser.get_env_var(env_variable, value)
                li_settings_values.append(value)
            except TypeError:
                li_settings_values.append(
                    settings.value(key=i.name, defaultValue=i.default)
                )

        # instanciate new settings object
        options = PlgSettingsStructure(*li_settings_values)

        settings.endGroup()

        return options

    @staticmethod
    def get_value_from_key(key: str, default=None, expected_type=None) -> None | Any:
        """Return the value of a plugin setting by its key.

        :param key: setting key, must be an attribute of PlgSettingsStructure
        :type key: str
        :param default: fallback value if the key is not found, defaults to None
        :type default: Any, optional
        :param expected_type: expected type for deserialization by QgsSettings, defaults to None
        :type expected_type: type or None, optional

        :return: setting value, or None if the key is invalid or an error occurred
        :rtype: Any
        """
        if not hasattr(PlgSettingsStructure, key):
            log_hdlr.PlgLogger.log(
                message="Bad settings key. Must be one of: {}".format(
                    ",".join(f.name for f in fields(PlgSettingsStructure))
                ),
                log_level=Qgis.MessageLevel.Warning,
            )
            return None

        settings = QgsSettings()
        settings.beginGroup(__title__)

        try:
            out_value = settings.value(
                key=key, defaultValue=default, type=expected_type
            )
        except Exception as err:
            log_hdlr.PlgLogger.log(
                message=f"Error occurred trying to get settings: {key}. Trace: {err}",
                log_level=Qgis.MessageLevel.Warning,
                push=False,
            )
            out_value = None

        settings.endGroup()

        return out_value

    @classmethod
    def set_value_from_key(cls, key: str, value) -> bool:
        """Set plugin setting value using the key.

        :param key: setting key, must be an attribute of PlgSettingsStructure
        :type key: str
        :param value: value to set
        :type value: Any

        :return: True if the value was saved successfully, False otherwise
        :rtype: bool
        """
        if not hasattr(PlgSettingsStructure, key):
            log_hdlr.PlgLogger.log(
                message="Bad settings key: {}. Must be one of: {}".format(
                    key, ",".join(f.name for f in fields(PlgSettingsStructure))
                ),
                log_level=Qgis.MessageLevel.Critical,
            )
            return False

        settings = QgsSettings()
        settings.beginGroup(__title__)

        try:
            settings.setValue(key, value)
            out_value = True
            log_hdlr.PlgLogger.log(
                message=f"Setting `{key}` saved with value `{value}`",
                log_level=Qgis.MessageLevel.NoLevel,
            )
        except Exception as err:
            log_hdlr.PlgLogger.log(
                message=f"Error occurred trying to set settings: {key}. Trace: {err}",
                log_level=Qgis.MessageLevel.Warning,
                push=False,
            )
            out_value = False

        settings.endGroup()

        return out_value

    @classmethod
    def save_from_object(cls, plugin_settings_obj: PlgSettingsStructure) -> None:
        """Save plugin settings from a PlgSettingsStructure object.

        :param plugin_settings_obj: settings object to persist
        :type plugin_settings_obj: PlgSettingsStructure
        """
        for k, v in asdict(plugin_settings_obj).items():
            cls.set_value_from_key(k, v)
