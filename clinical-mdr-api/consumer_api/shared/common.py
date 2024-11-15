import logging
import os
import urllib.parse
from datetime import datetime
from typing import Any

import neo4j
from neomodel.sync_.core import db

from consumer_api.shared import config, exceptions

APP_ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))


log = logging.getLogger(__name__)


def load_env(key: str, default: str | None = None):
    value = os.environ.get(key)
    log.info("ENV variable fetched: %s=%s", key, value)
    if value is None and default is None:
        log.error("%s is not set and no default was provided", key)
        raise EnvironmentError(f"Failed because {key} is not set.")
    if value is not None:
        return value
    log.warning("%s is not set, using default value: %s", key, default)
    return default


def query(
    cypher_query,
    params: dict = None,
    handle_unique: bool = True,
    retry_on_session_expire: bool = False,
    resolve_objects: bool = False,
    to_dict_list: bool = True,
):
    """
    Wraps `db.cypher_query()`

    Returns:
    list[dict] | tuple: If `to_dict_list` is True, returns a list of dictionaries representing the query results.
                        If `to_dict_list` is False, returns a tuple containing the rows and columns from the query.
    """
    rows, columns = db.cypher_query(
        query=cypher_query,
        params=params,
        handle_unique=handle_unique,
        retry_on_session_expire=retry_on_session_expire,
        resolve_objects=resolve_objects,
    )

    if to_dict_list:
        return [get_db_result_as_dict(row, columns) for row in rows]

    return rows, columns


def validate_page_number_and_page_size(page_number: int, page_size: int):
    # neo4j supports `SKIP {val}` values which fall within unsigned 64-bit integer range
    if (page_number - 1) * page_size >= config.MAX_INT_NEO4J:
        raise exceptions.ValidationException(
            f"(page_number * page_size) value cannot be bigger than {config.MAX_INT_NEO4J}"
        )


def urlencode_link(link: str) -> str:
    """URL encodes a link"""

    url = urllib.parse.urlparse(link)
    query_params = urllib.parse.parse_qs(url.query, keep_blank_values=True)

    url = url._replace(query=urllib.parse.urlencode(query_params, True))
    return urllib.parse.urlunparse(url)


def get_db_result_as_dict(row: list[Any], columns: list[str]) -> dict:
    item = {}
    for key, value in zip(columns, row):
        item[key] = value
    return item


def db_pagination_clause(page_size: int, page_number: int) -> str:
    return f"SKIP {page_number - 1} * {page_size} LIMIT {page_size}"


def db_sort_clause(sort_by: str, sort_order: str = "ASC") -> str:
    return f"ORDER BY toLower({sort_by}) {sort_order}"


def get_api_version() -> str:
    version_path = os.path.join("./consumer_api", "apiVersion")
    with open(version_path, "r", encoding="utf-8") as file:
        return file.read().strip()


def strtobool(value: str) -> int:
    """Convert a string representation of truth to integer 1 (true) or 0 (false).

    Returns 1 for True values: 'y', 'yes', 't', 'true', 'on', '1'.
    Returns 0 for False values: 'n', 'no', 'f', 'false', 'off', '0'.
    Otherwise raises ValueError.

    Reimplemented because of deprecation https://peps.python.org/pep-0632/#migration-advice

    Returns int to remain compatible with Python 3.7 distutils.util.strtobool().
    """

    val = value.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return 1
    if val in ("n", "no", "f", "false", "off", "0"):
        return 0
    raise ValueError(f"invalid truth value: {value:s}")


def convert_to_datetime(value: neo4j.time.DateTime) -> datetime | None:
    """
    Converts a DateTime object from the database to a Python datetime object.

    Args:
        value (neo4j.time.DateTime): The DateTime object to convert.

    Returns:
        datetime: The Python datetime object.
    """
    return value.to_native() if value is not None else None
