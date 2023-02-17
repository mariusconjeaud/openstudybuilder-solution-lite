from typing import Optional, Sequence, Any
import logging

logger = logging.getLogger("legacy_mdr_migrations")
# ---------------------------------------------------------------
# Utilites for parsing and converting data
# ---------------------------------------------------------------
#

def parse_to_int(s: str) -> int:
    try:
        return int(s)
    except ValueError:
        logger.warning("Failed to parse %s to integer, defaulting to 0", s)
        return 0


def title_case(s: str) -> str:
    exceptions = ["And", "Or", "The", "A", "Of", "In"]
    words = s.title().split(" ")
    return " ".join(
        [words[0]]
        + [word.lowercase() if word in exceptions else word for word in words[1:]]
    )


def parse_float(value: str) -> Optional[float]:
    # SAS DEFAULT for NULL is "."
    if value.lower() in (".", "null", "none"):
        return None
    try:
        new_value = float(value.replace("E", "e"))
    except ValueError:
        new_value = 0.0
        logger.warning(f"Unable to parse string '{value}' as a number, defaulting to {new_value}")
    return new_value


def map_boolean(bool_str: str, raise_exception=False) -> bool:
    if bool_str in ("Y", "y", "T", "True", "TRUE", "true"):
        return True
    elif bool_str in ("N", "n", "F", "False", "FALSE", "false"):
        return False
    else:
        if raise_exception:
            raise ValueError(f"Unable to map string :'{bool_str}' to a boolean value")
        logger.warning(
            f"Unable to map string :'{bool_str}' to a boolean value, default is set to false"
        )
        return False


def find_term_by_name(term_name: str, all_terms: Sequence[dict]) -> Optional[str]:
    term_uid = None
    for term in all_terms:
        if term["name"]["sponsor_preferred_name"].lower() == term_name.lower():
            term_uid = term["term_uid"]
            break
        elif term["attributes"]["code_submission_value"] is not None:
            if term["attributes"]["code_submission_value"].lower() == term_name.lower():
                term_uid = term["term_uid"]
                break
        elif term["attributes"]["name_submission_value"] is not None:
            if term["attributes"]["name_submission_value"].lower() == term_name.lower():
                term_uid = term["term_uid"]
                break
    return term_uid


def update_uid_list_dict(key: str, dictionary: dict, value_to_add: Any):
    if key not in dictionary:
        dictionary[key] = [value_to_add]
    else:
        dictionary[key].append(value_to_add)
