"""Handles interactions with the config file."""
from pathlib import Path
from typing import cast

import tomlkit

from .datatypes import ConfigDataType, columns_available


def find_config() -> Path:
    """Find `config.toml` and return a Path representing it."""
    return Path(__file__).with_name("config.toml")


def load_config() -> ConfigDataType:
    """Read config file and return values as dictionary."""
    with find_config().open("r") as file:
        return cast(ConfigDataType, tomlkit.parse(file.read()))


def write_config(config_data: ConfigDataType) -> None:
    """Write specified config data to `config.toml`.

    :param config_data: config data to be written; make sure this is a tomlkit object
    that includes comments.
    """
    with find_config().open("w") as file:
        file.write(tomlkit.dumps(config_data))


def min_widths(config_data: ConfigDataType) -> dict[columns_available, int]:
    """Extract list of minimum widths from configuration data.

    Returns the column widths for columns listed in `columns`.
    """
    return {
        key: config_data["available_columns"][key]["min_width"]
        for key in config_data["columns"]
    }


def max_widths(config_data: ConfigDataType) -> dict[columns_available, int]:
    """Extract list of maximum widths from configuration data.

    Returns the column widths for columns listed in `columns`.
    """
    return {
        key: config_data["available_columns"][key]["max_width"]
        for key in config_data["columns"]
    }


def flexibility(config_data: ConfigDataType) -> dict[columns_available, int | float]:
    """Extract list of flexibilities from configuration data.

    Returns the column widths for columns listed in `columns`.
    """
    return {
        key: config_data["available_columns"][key]["flexibility"]
        for key in config_data["columns"]
    }
