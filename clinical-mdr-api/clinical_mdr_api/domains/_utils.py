import re
from enum import Enum
from typing import Sequence

from bs4 import BeautifulSoup

from clinical_mdr_api import exceptions
from clinical_mdr_api.domains.iso_languages import LANGUAGES_INDEXED_BY


class ObjectStatus(Enum):
    """
    Enum for object status.

    Possible values:
    - LATEST_FINAL: The latest final version of the object.
    - LATEST_RETIRED: The latest retired version of the object.
    - LATEST_DRAFT: The latest draft version of the object.
    - LATEST: The latest version of the object, regardless of the status.
    """

    LATEST_FINAL = "final"
    LATEST_RETIRED = "retired"
    LATEST_DRAFT = "draft"
    LATEST = "latest"


def generate_seq_id(
    uid: str,
    parent_sequence_id: str | None = None,
    custom_abbr: str | None = None,
    next_available_sequence_id: str | None = None,
):
    """
    Generates a sequence ID based on the provided parameters.

    Args:
        uid (str): UID of the Node.
        parent_sequence_id (str | None, optional): Parent sequence ID to prepend to generated the sequence ID. Defaults to None.
        custom_abbr (str | None, optional): Custom abbreviation to use instead of the first uppercase letters of the UID. Defaults to None.

    Returns:
        str: Generated sequence ID.

    Example:
        >>> generate_seq_id("SEQ_003", parent_sequence_id="B1", custom_abbr="ABC")
        "B1ABC3"
    """

    def extract_seq_number_from_uid(uid: str):
        if "_" in uid:
            return uid.split("_", 1)[1].lstrip("0")
        return uid

    def get_seq_name_abbr(uid: str):
        if custom_abbr:
            return custom_abbr

        name = uid.replace("Template", "")

        return "".join([char for char in name if char.isupper()])

    if next_available_sequence_id:
        return next_available_sequence_id

    seq_id = get_seq_name_abbr(uid) + extract_seq_number_from_uid(uid)

    if parent_sequence_id:
        seq_id = parent_sequence_id + seq_id

    return seq_id


def get_iso_lang_data(
    q: str,
    key: str = "639-3",
    return_key: str | None = None,
    ignore_case: bool = True,
) -> str | dict | list:
    """
    Returns ISO language data based on the provided query string and key.

    Args:
        q (str): Query string to search for in the language index.
        key (str, optional): Key to use for indexing the language data. Defaults to "639-3".
        return_key (str | None, optional): Key to return from the found language data. Defaults to None.
        ignore_case (bool, optional): Whether to ignore case when searching for the query string. Defaults to True.

    Returns:
        str | dict | list: The value of the found language data, or the entire language data if return_key is None.

    Raises:
        TypeError: If the query string is not a string.
        ValueError: If the provided key is not a valid index for the language data.
        KeyError: If the query string is not found in the language index, or if it is found but does not match the query when ignore_case is False.

    Example:
        >>> get_iso_lang_data("spa", "639-2/T", "names")
        ["Spanish", "Castilian"]
    """
    if not isinstance(q, str):
        raise TypeError(f"Expected type str but found {type(q)}")

    try:
        index = LANGUAGES_INDEXED_BY[key]
    except KeyError as exc:
        raise exceptions.ValidationException(
            f"Languages not indexed by key: {key}"
        ) from exc

    q_ = q.casefold()

    try:
        lang = index[q_]
    except KeyError as exc:
        raise KeyError(q) from exc

    if not ignore_case and lang[key] != q:
        raise KeyError(q)

    return lang[return_key] if return_key else lang


def normalize_string(s: str | None) -> str | None:
    """
    Normalizes a string by stripping whitespace and returning None if the resulting string is empty.

    Args:
        s (str | None): The string to normalize.

    Returns:
        str | None: The normalized string, or None if the resulting string is empty.

    Example:
        >>> normalize_string("   hello world   ")
        "hello world"
    """
    if s:
        s = s.strip()
    return s or None


def strip_html(html: str) -> str:
    """
    Removes HTML tags from a string.

    Args:
        html (str): The string containing HTML tags.

    Returns:
        str: The string with HTML tags removed.

    Example:
        >>> strip_html("<p>Some <b>bold</b> text.</p>")
        "Some bold text."
    """
    return BeautifulSoup(html, "lxml").text


def convert_to_plain(text: str) -> str:
    """
    Converts a text with HTML tags and square brackets to plain text.

    Args:
        text (str): The text to convert.

    Returns:
        str: The plain text.

    Example:
        >>> convert_to_plain("<p>Some [text] with <b>HTML</b> tags.</p>")
        "Some text with HTML tags."
    """
    return strip_html(text).replace("[", "").replace("]", "")


def extract_parameters(name: str) -> Sequence[str]:
    """
    Extracts parameters from a string. A parameter is a string that is between two square brackets.

    Args:
        name (str): The string to extract parameters from.

    Returns:
        Sequence[str]: A sequence of parameter names.

    Example:
        >>> extract_parameters("Some [parameter1] and [parameter2]")
        ["parameter1", "parameter2"]
    """
    return re.findall(r"\[([\w\s\-]+)]", name)


def is_syntax_of_template_name_correct(name: str) -> bool:
    """
    Checks the syntax of the name.
    The syntax is considered to be valid if all of the following conditions are true:
    - The name consists of at least one printable character.
    - The name contains no brackets or a matching number of opening and closing brackets [].
    - The name does not contain nested brackets like this: [a[b]c].
    - The parameters within the brackets need to consist of at least one character.

    Args:
        name (str): The name of the template.

    Returns:
        bool: True if the syntax of the name is valid.
    """
    if not isinstance(name, str):
        raise TypeError(f"Expected type str but found {type(name)}")

    if len(name.strip()) == 0:
        return False

    brackets_counter = 0
    char_counter = 0
    for char in name:
        if char == "[":
            brackets_counter += 1
            char_counter = 0
        elif char == "]":
            if char_counter == 0:
                return False
            brackets_counter -= 1
            char_counter = 0
        else:
            char_counter += 1

        if brackets_counter < 0 or brackets_counter > 1:
            return False

    return brackets_counter == 0


def factorize_dict(data: dict) -> dict:
    """
    Factorizes a dictionary by adding underscores to keys that do not start with an underscore.

    Args:
        data (dict): The dictionary to factorize.

    Returns:
        dict: The factorized dictionary.

    Example:
        >>> factorize_dict({"key1": 1, "_key2": 2, "key3": 3})
        {"_key1": 1, "_key2": 2, "_key3": 3}
    """
    return_dict = {}
    for key, value in data.items():
        new_key = key if key.startswith("_") else "_" + key
        return_dict[new_key] = value
    return return_dict


def defactorize_dict(data: dict) -> dict:
    """
    Defactorizes a dictionary by removing underscores from keys that start with an underscore.

    Args:
        data (dict): The dictionary to defactorize.

    Returns:
        dict: The defactorized dictionary.

    Example:
        >>> defactorize_dict({"_key1": 1, "key2": 2, "_key3": 3})
        {"key1": 1, "key2": 2, "key3": 3}
    """
    return_dict = {}
    for key, value in data.items():
        new_key = key[1:] if key.startswith("_") else key
        return_dict[new_key] = value
    return return_dict
