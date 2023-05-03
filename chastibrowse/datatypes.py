"""Datatypes representing various json structures."""

from typing import Literal, NotRequired, TypedDict

columns_available = Literal[
    "maxtime",
    "password_needed",
    "name",
    "description",
    "description_len",
    "link",
    "lock_id",
    "keyholder_name",
    "keyholder_gender",
]


class ColumnConfigDataType(TypedDict):
    """Represents a single column in the [columns] table in `config.toml`."""

    name: str
    min_width: int
    flexibility: int | float
    max_width: int


class ColumnsListDataType(TypedDict):
    """Represents the [columns] table of `config.toml`."""

    maxtime: ColumnConfigDataType
    password_needed: ColumnConfigDataType
    name: ColumnConfigDataType
    description: ColumnConfigDataType
    description_len: ColumnConfigDataType
    link: ColumnConfigDataType
    lock_id: ColumnConfigDataType
    keyholder_name: ColumnConfigDataType
    keyholder_gender: ColumnConfigDataType


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
    show_suspended_keyholders: bool
    links: LinksConfigDataType
    blacklists: BlacklistConfigDataType


class FormattingConfigDataType(TypedDict):
    """Represents the [formatting] table of `config.toml`."""

    remove_emojis: bool
    enforce_ascii: bool


class ConfigDataType(TypedDict):
    """Represents `config.toml`."""

    amount_to_fetch: int
    show_keyholder_names: bool
    columns: list[columns_available]
    formatting: FormattingConfigDataType
    criteria: CriteriaDataType
    available_columns: ColumnsListDataType


class UserJsonType(TypedDict):
    """Represents a chaster.app user json dict."""

    _id: str
    username: str
    isFindom: bool
    gender: str | None
    isSuspendedOrDisabled: bool


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
