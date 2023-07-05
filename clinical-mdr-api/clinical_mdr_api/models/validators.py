"""Reusable pydantic validator functions"""
from clinical_mdr_api.exceptions import ValidationException


# pylint: disable=unused-argument
def validate_string_represents_boolean(cls, value, values, field):
    if not value:
        return "false"

    truthy = ("y", "yes", "t", "true", "on", "1")
    falsy = ("n", "no", "f", "false", "off", "0")

    if value.lower() not in (truthy + falsy):
        raise ValidationException(
            f"Unsupported boolean value '{value}' for field '{field.name}'. Allowed values are: {truthy + falsy}."
        )

    return value
