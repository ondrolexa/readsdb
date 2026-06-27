import os
from typing import TypeVar

T = TypeVar("T")


class EnvVarParser:
    """Utility class to retrieve and convert environment variables."""

    @staticmethod
    def get_env_var(name: str, default: T) -> T:
        """Retrieves an environment variable and converts it based on the default value type.

        :param name: The environment variable name
        :type name: str
        :param default: The default value, used to infer the expected type
        :type default: T
        :return: The converted value, matching the type of `default`
        :rtype: T
        """
        value = os.getenv(name)
        if value is None:
            return (
                default  # Return the default value if the environment variable is not
            )

        # Otherwise, treat it as a single value
        return EnvVarParser._convert_single(value, type(default), default)

    @staticmethod
    def _convert_single(value: str, expected_type: type[T], default: T) -> T:
        """Converts a string into a single value of the expected type.

        :param value: value as string
        :type value: str
        :param expected_type: expected type for conversion (int, float, bool)
        :type expected_type: type[T]
        :param default: default value in case of conversion failure
        :type default: T
        :raises TypeError: Exception raised when expected_type is not compatible
        :return: string value converted to expected_type
        :rtype: T
        """
        try:
            if expected_type is int:
                return int(value)
            elif expected_type is float:
                return float(value)
            elif expected_type is bool:
                return EnvVarParser._convert_bool(value, default)
            elif expected_type is str:
                return value  # String value
        except ValueError:
            return default  # Return default value in case of conversion failure

        raise TypeError(
            f"Unsupported type: {expected_type}. Value definition from environment variable is not possible."
        )

    @staticmethod
    def _convert_bool(value: str, default: bool) -> bool:
        """Converts a string into a boolean, handling explicit True/False values.

        :param value: input string value
        :type value: str
        :param default: default value if conversion fails
        :type default: bool
        :return: converted str as bool
        :rtype: bool
        """
        true_values = {"1", "true", "yes", "on"}
        false_values = {"0", "false", "no", "off"}
        value_lower = value.lower()

        if value_lower in true_values:
            return True
        elif value_lower in false_values:
            return False
        return default  # Return default value if conversion fails
