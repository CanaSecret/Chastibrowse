"""Handles tabular printing of information, scaling to terminal width."""
import math
import os

import emoji

from .config_helper import flexibility, max_widths, min_widths
from .datatypes import ConfigDataType, columns_available


def asciiify(text: str) -> str:
    """Encode a string with ascii and decode. Removes all emojis and other special symbols."""
    return text.encode("ascii", errors="ignore").decode("ascii")


def clean(text: str) -> str:
    """Remove emojis from given text."""
    return emoji.replace_emoji(text, replace="")


def fixed_length(text: str, length: int) -> str:
    """Format a string to a fixed length, cutting off with elipsis or padding as needed."""
    text = text.strip()
    text = text.replace("\n", " ")
    if len(text) == length:
        return text
    if len(text) > length:
        return text[: length - 1] + "…"
    return f"{text:<{length}}"  # pad with spaces


def generate_border(widths: list[int]) -> str:
    """Generate a table border of spaces and hyphens from a list of column widths."""
    border = ""
    for width in widths:
        border += "-" * width + "  "
    return border


def split_spare_columns(
    amount: int,
    weights: dict[columns_available, int | float],
    maxes: dict[columns_available, int],
) -> dict[columns_available, int]:
    """Given `amount` columns, a list of weights and maxima, split the spare columns up.

    :param amount: amount of spare columns to divide up
    :param weights: dict of keys as col names, ints or floats representing weights of table columns
    :param maxes: dict of keys as col names, ints representing max columns per table column
    """
    amount_remaining = amount
    cols_remaining = list(weights.keys())
    result: dict[columns_available, int] = {}
    denominator = sum(weights.values())

    # remove columns if weight = 0
    for key, weight in weights.items():
        if weight == 0:
            result[key] = 0
            cols_remaining.remove(key)
            continue

    # sort out columns that recieve their max value
    old_amount = None
    while old_amount != amount_remaining:
        to_complete = []
        old_amount = amount_remaining
        for key in cols_remaining:
            if maxes[key] == 0:  # if no max set, we can't reach it
                continue
            if math.floor(amount_remaining / denominator * weights[key]) >= maxes[key]:
                to_complete.append(key)
                continue  # if we can assign max space, do so
        for key in to_complete:
            result[key] = maxes[key]
            amount_remaining -= maxes[key]
            denominator -= weights[key]
            cols_remaining.remove(key)
    if not cols_remaining:  # if we're done
        return result

    # non-maxed columns
    for key in cols_remaining:
        result[key] = math.floor(amount_remaining / denominator * weights[key])
    return {key: result[key] for key in weights}


def table(
    data: list[list[str]],
    config: ConfigDataType,
) -> str:
    """Format a table similarly to `tabulate.tabulate`.

    :param min_widths: minimum widths for each column.

    :param flexibility: list with an element for each column;
    value represents weight of available space given to element; set to 0 to lock width

    :param data: list of rows, given as a list of strings containing the data to be printed
    """
    spare_cols = (
        os.get_terminal_size().columns
        - sum(min_widths(config).values())
        - 2 * (len(config["columns"]) - 1)  # 2 spaces per gap
        - 3  # 3 safety buffer
    )

    additional_widths = split_spare_columns(
        spare_cols, flexibility(config), max_widths(config)
    )

    true_widths = {
        col: config["available_columns"][col]["min_width"] + additional_widths[col]
        for col in config["columns"]
    }

    output_lines: list[str] = [generate_border(list(true_widths.values()))]
    if config["formatting"]["enforce_ascii"]:
        data = [[asciiify(item) for item in row] for row in data]
    elif config["formatting"][
        "remove_emojis"
    ]:  # if ascii was called this can be skipped
        data = [[clean(item) for item in row] for row in data]
    for row in data:
        output_lines.append(
            "  ".join(
                [
                    fixed_length(item, list(true_widths.values())[i])
                    for i, item in enumerate(row)
                ]
            )
        )
    output_lines.append(generate_border(list(true_widths.values())))
    return "\n".join(output_lines)
