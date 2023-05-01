"""Simple user interface and entry point."""

import os
import sys
import time
from pathlib import Path
from typing import cast

import tomllib

from . import chaster, format_table
from .datatypes import ConfigDataType


def load_config() -> ConfigDataType:
    """Read config file and return values as dictionary."""
    path = Path(__file__).with_name("config.toml")
    with path.open("rb") as file:
        return cast(ConfigDataType, dict(tomllib.load(file)))


def main() -> None:
    """Run CLI."""
    config_data = load_config()
    if os.get_terminal_size().columns < sum(config_data["formatting"]["min_widths"]):
        print(
            "Your terminal is very thin! If you can, make it wider, then reload.\n" * 5
        )
        time.sleep(3)
    lastid = None
    while True:
        newlocks = chaster.fetch_locks(config_data["amount_to_fetch"], lastid)

        table = []
        for lock in newlocks:
            if not lock.invalid(config_data["criteria"]):
                table.append(lock.to_list())

        lastid = newlocks[-1].id

        print(format_table.table(data=table, config=config_data["formatting"]))
        lock_id_length = len(newlocks[0].id)  # should always be 24

        operation = input(
            f"code: {lastid} | paste code to load | press enter | 'quit' / 'reload' / 'config' | > "
        ).casefold()
        if operation in [
            "q",
            "quit",
            "exit",
        ]:
            sys.exit(0)
        elif len(operation) == lock_id_length:  # length of lock id
            lastid = operation
        elif operation == "reload":
            main()
            sys.exit(0)
        elif operation == "config":
            print(
                f"\nYour config file is located at {str(Path(__file__).with_name('config.toml'))}\n"
            )
            time.sleep(3)


if __name__ == "__main__":
    main()
