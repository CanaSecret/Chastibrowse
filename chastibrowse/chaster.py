"""Interface between Chastibrowse and chaster.app."""

from __future__ import annotations

import datetime
import json
from typing import TYPE_CHECKING

import requests
from dateutil import parser

if TYPE_CHECKING:
    from .datatypes import (
        ContentDataType,
        CriteriaDataType,
        LockJsonType,
        PostDataType,
        UserJsonType,
        columns_available,
    )


class ChasterError(Exception):
    """Represents an error given back by chaster.app."""


class ChasterUser:
    """Python representation of a chaster.app user. Only contains used fields."""

    def __init__(
        self: ChasterUser,
        _id: str,
        name: str,
        findom: bool,
        gender: str,
        discord: str | None,
        disabled: bool,
    ) -> None:
        """ChasterUser constructor.

        :param _id: chaster.app id of the user, given as a hex string
        :param name: user's username
        :param findom: whether the user has marked themselves as findom
        :param gender: the user's selected gender; may be an empty string

        :return: None
        """
        self.id = _id
        self.name = name
        self.findom = findom
        self.gender = gender
        self.discord = discord
        self.suspended = disabled

    @classmethod
    def from_json(cls: type[ChasterUser], data: UserJsonType) -> ChasterUser:
        """Create a ChasterUser object from a dict containing the needed info."""
        gender = (
            ""
            if data["gender"] is None or data["gender"].strip() in ["", "Not specified"]
            else data["gender"]
        )
        return ChasterUser(
            data["_id"],
            data["username"],
            data["isFindom"],
            gender,
            data["discordUsername"],
            data["isSuspendedOrDisabled"],
        )


class ChasterLock:
    """Python representation of a chaster.app public lock. Only contains used fields."""

    def __init__(
        self: ChasterLock,
        _id: str,
        name: str,
        desc: str,
        maxtime: int | None,
        password_needed: bool,
        keyholder: ChasterUser,
    ) -> None:
        """`ChasterLock` constructor.

        :param _id: chaster.app id of the lock, given as a hex string
        :param name: the lock's title
        :param desc: the lock's description
        :param maxtime: the maximum lock time from object creation in seconds
        :param password_needed: is a password required to join this lock?
        :param keyholder: the lock's keyholder, as a `ChasterUser`

        :return None:
        """
        self.id = _id
        self.name = name
        self.desc = desc
        self.maxtime = maxtime
        self.password_needed = password_needed
        self.keyholder = keyholder

    def invalid(self: ChasterLock, criteria: CriteriaDataType) -> bool:
        """Check the given criteria with itself to determine eligibility."""
        if (
            len(self.desc) < criteria["minimum_description_length"]
            or ((not criteria["show_findom"]) and self.keyholder.findom)
            or (
                self.maxtime is not None and self.maxtime > criteria["max_max_time"] > 0
            )
            or (self.maxtime is None and criteria["max_max_time"] > 0)
            or (
                not (criteria["links"]["show_linked_titles"])
                and "chaster.app" in self.name
            )
            or (
                not (criteria["links"]["show_linked_descriptions"])
                and "chaster.app" in self.desc.casefold()
            )
            or (
                not (criteria["links"]["show_desc_startswith_link"])
                and self.desc.casefold().startswith("https://chaster.app")
            )
            or (
                self.keyholder.name.casefold()
                in map(str.casefold, criteria["blacklists"]["users"])
            )
            or (
                self.keyholder.gender.casefold()
                in map(str.casefold, criteria["blacklists"]["keyholder_genders"])
            )
            or (
                not (criteria["show_suspended_keyholders"]) and self.keyholder.suspended
            )
            or (criteria["require_connected_discord"] and not (self.keyholder.discord))
        ):
            return True
        return any(
            word.casefold() in self.name.casefold() or word in self.desc
            for word in criteria["blacklists"]["keywords"]
        )

    def format_max_time(self: ChasterLock) -> str:
        """Represent the maximum time in either days, hours or minutes."""
        if not self.maxtime:
            return "None"
        if self.maxtime >= 60 * 60 * 24:
            return f"{round(self.maxtime / (60 * 60 * 24))}d"
        if self.maxtime >= 60 * 60:
            return f"{round(self.maxtime / (60 * 60))}h"
        return f"{round(self.maxtime / 60)}m"

    def link(self: ChasterLock) -> str:
        """Generate a link to itself."""
        return f"https://chaster.app/explore/{self.id}"

    def to_list(self: ChasterLock, columns: list[columns_available]) -> list[str]:
        """Return a list containing lock information to be shown."""
        row: list[str] = []
        options: dict[columns_available, str] = {
            "maxtime": self.format_max_time(),
            "password_needed": "*" if self.password_needed else " ",
            "name": self.name,
            "description": self.desc,
            "description_len": str(len(self.desc)),
            "link": self.link(),
            "lock_id": self.id,
            "keyholder_name": self.keyholder.name,
            "keyholder_gender": self.keyholder.gender,
            "discord": self.keyholder.discord if self.keyholder.discord else "",
        }
        for col in columns:
            row.append(options[col])
        return row

    @classmethod
    def from_json(cls: type[ChasterLock], data: LockJsonType) -> ChasterLock:
        """Create a ChasterLock from a dict containing the needed info."""
        if data["maxLimitDuration"]:
            maxtime = data["maxLimitDuration"]
        elif data["maxLimitDate"]:
            maxtime = int(
                (
                    parser.parse(data["maxLimitDate"]).replace(tzinfo=None)
                    - datetime.datetime.now(tz=None)
                ).total_seconds()
            )
        else:
            maxtime = None
        return cls(
            data["_id"],
            data["name"],
            data["description"],
            maxtime,
            data["requirePassword"],
            ChasterUser.from_json(data["user"]),
        )


def fetch_locks(amount: int, previous_id: str | None = None) -> list[ChasterLock]:
    """Fetch and return chaster.app locks; starting at a certain id and going backwards in time.

    :param amount: An integer representing the amount of locks to fetch.
    The chaster.app API will refuse requsts of more than 100.
    :param previous_id: The id of the last lock fetched. This lock will not be returned.

    :return: List of ChasterLock objects representing all locks returned by the API.
    """
    minimum_amount, maximum_amount = 1, 100
    if amount < minimum_amount:
        raise ValueError(f"`amount` is less than {minimum_amount}") from AssertionError
    if amount > maximum_amount:
        raise ValueError(f"`amount` is more than {maximum_amount}") from AssertionError

    post_data: PostDataType = {"limit": amount}
    if previous_id:
        post_data["lastId"] = previous_id

    response = requests.post(
        "https://api.chaster.app/public-locks/search", json=post_data, timeout=10
    )

    resp_data: ContentDataType = json.loads(response.content)

    success = 200
    if response.status_code == success:
        return [ChasterLock.from_json(json_data) for json_data in resp_data["results"]]
    raise ChasterError(f"error {response.status_code}: {resp_data['message']}")
