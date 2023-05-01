"""Handles tabular printing of information, scaling to terminal width."""
import math
import os

import emoji

from .datatypes import FormattingConfigDataType


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


def table(
    data: list[list[str]],
    config: FormattingConfigDataType,
) -> str:
    """Format a table similarly to `tabulate.tabulate`.

    :param min_widths: minimum widths for each column.

    :param flexibility: list with an element for each column;
    value represents weight of available space given to element; set to 0 to lock width

    :param data: list of rows, given as a list of strings containing the data to be printed
    """
    n_data_columns = len(data[0])
    for row in data[1:]:
        if len(row) != n_data_columns:
            raise ValueError("All rows must have the same length.")

    if (
        len(config["min_widths"]) < n_data_columns
        or len(config["flexibility"]) < n_data_columns
    ):
        raise ValueError(
            "Minimum widths and flexibility must be at least as long as data."
        )

    spare_cols = (
        os.get_terminal_size().columns
        - sum(config["min_widths"][:n_data_columns])
        - 2 * (n_data_columns - 1)  # 2 spaces per gap
        - 3  # 3 safety buffer
    )
    true_widths: list[int] = []
    for i in range(n_data_columns):
        true_widths.append(
            math.floor(
                spare_cols
                * config["flexibility"][i]
                / sum(config["flexibility"][:n_data_columns])
                + config["min_widths"][i]
            )
        )
    output_lines: list[str] = [generate_border(true_widths[:n_data_columns])]
    if config["enforce_ascii"]:
        data = [[asciiify(item) for item in row] for row in data]
    elif config["remove_emojis"]:  # if ascii was called this can be skipped
        data = [[clean(item) for item in row] for row in data]
    for row in data:
        output_lines.append(
            "  ".join(
                [fixed_length(item, true_widths[i]) for i, item in enumerate(row)]
            )
        )
    output_lines.append(generate_border(true_widths))
    return "\n".join(output_lines)
