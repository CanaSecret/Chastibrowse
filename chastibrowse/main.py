"""Simple user interface and entry point."""

import os
import sys
import time
from pathlib import Path

import pkg_resources

from . import chaster, format_table
from .config_helper import load_config, min_widths, write_config
from .datatypes import ConfigDataType


def handle_user_input(
    user_input: str,
    config_data: ConfigDataType,
    newlocks: list[chaster.ChasterLock],
    lastid: str | None,
) -> str | None:
    """Handle the given user command and return a new `lastid` depending on the action taken.

    :param user_input: the given user command to handle
    :param config_data: a set of config data, as loaded by `load_config()`
    :param newlocks: list of new locks, used for determining last lock seen
    :param lastid: the previous `lastid`. will be returned if the same locks are to be loaded again.

    :return: Returns a new value for `lastid` depending on the action taken.
    """
    lock_id_length = len(newlocks[0].id)  # should always be 24

    if user_input in [
        "q",
        "quit",
        "exit",
    ]:
        sys.exit(0)
    elif user_input == "reload":
        main(lastid)  # restart at current shown locks
        sys.exit(0)
    elif user_input == "config":
        print(
            f"\nYour config file is located at {str(Path(__file__).with_name('config.toml'))}\n"
        )
        time.sleep(3)
        return lastid  # show previous locks
    elif user_input.startswith("blacklist"):
        username = user_input.split(" ")[1]
        if username not in config_data["criteria"]["blacklists"]["users"]:
            config_data["criteria"]["blacklists"]["users"].append(username)
            write_config(config_data)
        else:
            print("user already blacklisted!")
            time.sleep(1)
        return lastid  # show previous locks
    elif user_input.startswith("help"):
        print(
            "Press enter without any input to load more locks.\n"
            "Paste a save code to continue from where you left off.\n"
            "q | quit | exit      : Exits Chastibrowse.\n"
            "reload               : Reload Chastibrowse. Run after resizing terminal.\n"
            "config               : Find and show location of config file.\n"
            "blacklist [username] : Add a chaster.app username to the user blacklist.\n"
            "help                 : Show this message.\n"
            "\n"
            "Commands are not case-sensitive."
        )
        input("Press enter to return. ")
        return lastid  # show previous locks
    elif len(user_input) == lock_id_length:  # length of lock id
        return user_input  # load locks from user hash
    elif user_input:
        print("Command not recognized.")
        time.sleep(1)
        return lastid  # show previous locks
    else:
        return newlocks[-1].id  # load new locks


def main(lastid: str | None = None) -> None:
    """Run CLI."""
    config_data = load_config()
    if os.get_terminal_size().columns < sum(min_widths(config_data).values()):
        print(
            "Your terminal is very thin! If you can, make it wider, then reload.\n" * 5
        )
        time.sleep(3)
    while True:
        config_data = load_config()
        newlocks = chaster.fetch_locks(config_data["amount_to_fetch"], lastid)
        table: list[list[str]] = []
        for lock in newlocks:
            if not lock.invalid(config_data["criteria"]):
                table.append(lock.to_list(config_data["columns"]))
        if len(table) == 0:
            print(
                "All locks were excluded due to filters. "
                "Consider increasing `amount_to_fetch` if this happens often."
            )
            time.sleep(1)
            print("Loading more...")
            lastid = newlocks[-1].id
            continue

        if len(config_data["columns"]) == 0:
            print("Well, what did you expect to happen?")
            time.sleep(1)
        print(format_table.table(data=table, config=config_data))

        user_input = (
            input(
                f"(Chastibrowse {pkg_resources.get_distribution('chastibrowse').version}) | "
                f"Code: {lastid} | Enter 'help' | > "
            )
            .casefold()
            .strip()
        )

        lastid = handle_user_input(user_input, config_data, newlocks, lastid)


if __name__ == "__main__":
    main()
