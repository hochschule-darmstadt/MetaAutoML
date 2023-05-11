"""
Provides access to configuration

Explanation: This module defines where configuration values come from.
At the time of writing this was environment variables.
Switching to JSON only requires adaptions in this file.
"""

from os import environ as __environ


def get_config_value(key: str) -> str | None:
    """Gets the value of a config

    Args:
        key (str): the key of the config item

    Returns:
        str | None: The string value of the config item or None, if the config item doesn't exist
    """
    return __environ.get(key)
