import pytest

from consumer_api.shared import common, exceptions


def test_load_env():
    env_var1 = common.load_env("VAR1", "value1")
    assert env_var1 == "value1"

    env_var1 = common.load_env("VAR1", "")
    assert env_var1 == ""

    with pytest.raises(EnvironmentError) as exc_info:
        common.load_env("VAR1")
    assert str(exc_info.value) == "Failed because VAR1 is not set."


def test_strtobool():
    assert common.strtobool("True") == 1
    assert common.strtobool("true") == 1
    assert common.strtobool("TRUE") == 1
    assert common.strtobool("t") == 1
    assert common.strtobool("T") == 1
    assert common.strtobool("1") == 1

    assert common.strtobool("False") == 0
    assert common.strtobool("false") == 0
    assert common.strtobool("FALSE") == 0
    assert common.strtobool("f") == 0
    assert common.strtobool("F") == 0
    assert common.strtobool("0") == 0

    with pytest.raises(ValueError) as exc_info:
        common.strtobool("-invalid-")
    assert str(exc_info.value) == "invalid truth value: -invalid-"


@pytest.mark.parametrize(
    "page_number, page_size",
    [[1, 10], [2, 200], [3000, 1000], [9223372036854775807, 1]],
)
def test_validate_page_number_and_page_size(page_number, page_size):
    common.validate_page_number_and_page_size(page_number, page_size)


@pytest.mark.parametrize(
    "page_number, page_size",
    [[9223372036854775808, 1], [9223372036854775807, 10]],
)
def test_validate_page_number_and_page_size_negative(page_number, page_size):
    with pytest.raises(exceptions.ValidationException) as exc_info:
        common.validate_page_number_and_page_size(page_number, page_size)
    assert (
        str(exc_info.value)
        == "(page_number * page_size) value cannot be bigger than 9223372036854775807"
    )
