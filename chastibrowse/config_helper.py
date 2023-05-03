"""Handles interactions with the config file."""
from pathlib import Path
from typing import cast

import tomlkit
import typeguard

from .datatypes import ConfigDataType, columns_available


class ConfigError(Exception):
    """Exception for an incorrectly formatted config file."""


def find_config() -> Path:
    """Find `config.toml` and return a Path representing it."""
    return Path(__file__).with_name("config.toml")


def validate_config(config: ConfigDataType) -> bool:
    """Validate given config file."""
    try:
        typeguard.check_type(config.unwrap(), ConfigDataType)  # type: ignore[attr-defined]
    except typeguard.TypeCheckError as e:
        raise ConfigError from e
    # I really hate that type ignore statement above, but I don't see a better way.
    max_to_fetch = 100
    if not (1 <= config["amount_to_fetch"] <= max_to_fetch):
        raise ConfigError("`amount_to_fetch` must be between 1 and 100.")
    if len(config["columns"]) != len(set(config["columns"])):
        raise ConfigError("Can't have duplicated elements in `columns`.")
    for key in config["available_columns"]:
        key = cast(columns_available, key)
        if (
            config["available_columns"][key]["max_width"] != 0
            and config["available_columns"][key]["min_width"]
            > config["available_columns"][key]["max_width"]
        ):
            raise ConfigError(
                f"Max width of column {key} is smaller than minimum width."
            )
        if any(
            [
                config["available_columns"]["maxtime"]["min_width"] < 0,
                config["available_columns"][key]["max_width"] < 0,
                config["available_columns"][key]["flexibility"] < 0,
            ]
        ):
            raise ConfigError(f"One of {key}'s column values is negative.")

    return True


def load_config() -> ConfigDataType:
    """Read config file and return values as dictionary."""
    with find_config().open("r") as file:
        config = cast(ConfigDataType, tomlkit.parse(file.read()))
    validate_config(config)
    return config


def write_config(config_data: ConfigDataType) -> None:
    """Write specified config data to `config.toml`.

    :param config_data: config data to be written; make sure this is a tomlkit object
    that includes comments.

    :return: None
    """
    with find_config().open("w") as file:
        file.write(tomlkit.dumps(config_data))


def min_widths(config_data: ConfigDataType) -> dict[columns_available, int]:
    """Extract dictionary of column_name: minimum_width from configuration data.

    :return: the minimum column widths for columns listed in `columns`.
    """
    return {
        key: config_data["available_columns"][key]["min_width"]
        for key in config_data["columns"]
    }


def max_widths(config_data: ConfigDataType) -> dict[columns_available, int]:
    """Extract dictionary of column_name: maximum_width from configuration data.

    :return: the maximum column widths for columns listed in `columns`.
    """
    return {
        key: config_data["available_columns"][key]["max_width"]
        for key in config_data["columns"]
    }


def flexibility(config_data: ConfigDataType) -> dict[columns_available, int | float]:
    """Extract list of flexibilities from configuration data.

    :return: the column's flexibilities for columns listed in `columns`.
    """
    return {
        key: config_data["available_columns"][key]["flexibility"]
        for key in config_data["columns"]
    }
