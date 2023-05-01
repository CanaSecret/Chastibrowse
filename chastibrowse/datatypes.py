"""Datatypes representing various json structures."""

from typing import NotRequired, TypedDict


class LinksConfigDataType(TypedDict):
    """Represents the [criteria.links] table of `config.toml`."""

    show_linked_titles: bool
    show_linked_descriptions: bool
    show_desc_startswith_link: bool


class BlacklistConfigDataType(TypedDict):
    """Represents the [criteria.blacklists] table of `config.toml`."""

    users: list[str]
    keywords: list[str]
    keyholder_genders: list[str]


class CriteriaDataType(TypedDict):
    """Represents the [criteria] table of `config.toml`."""

    minimum_description_length: int
    show_findom: bool
    max_max_time: int
    links: LinksConfigDataType
    blacklists: BlacklistConfigDataType


class FormattingConfigDataType(TypedDict):
    """Represents the [formatting] table of `config.toml`."""

    remove_emojis: bool
    enforce_ascii: bool
    min_widths: list[int]
    flexibility: list[int]


class ConfigDataType(TypedDict):
    """Represents `config.toml`."""

    amount_to_fetch: int
    show_keyholder_names: bool
    formatting: FormattingConfigDataType
    criteria: CriteriaDataType


class UserJsonType(TypedDict):
    """Represents a chaster.app user json dict."""

    _id: str
    username: str
    isFindom: bool
    gender: str


class LockJsonType(TypedDict):
    """Represents a chaster.app lock json dict."""

    _id: str
    maxLimitDuration: int
    maxLimitDate: str
    name: str
    description: str
    requirePassword: bool
    user: UserJsonType


class PostDataType(TypedDict):
    """Represents the POST request data json."""

    limit: int
    lastId: NotRequired[str]


class ContentDataType(TypedDict):
    """Represents the content of the POST response."""

    count: int
    hasMore: bool
    results: list[LockJsonType]
    message: str
