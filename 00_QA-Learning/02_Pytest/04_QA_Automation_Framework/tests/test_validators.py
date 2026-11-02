import pytest

from app.exceptions import ValidationError
from app.validators import (
    validate_country_code,
    validate_non_negative,
    validate_number,
    validate_percentage,
    validate_positive,
    validate_quantity,
)

pytestmark = [pytest.mark.unit, pytest.mark.validation]


@pytest.mark.parametrize("value", [0, 1, -1, 2.5, -0.1])
def test_validate_number_accepts_numbers(value):
    assert validate_number(value) == value


@pytest.mark.parametrize("value", ["1", None, True, False, [], {}, float("nan"), float("-inf")])
def test_validate_number_rejects_invalid_values(value):
    with pytest.raises(ValidationError):
        validate_number(value)


def test_validation_error_is_a_value_error():
    with pytest.raises(ValueError):
        validate_number("abc")


def test_error_message_contains_field_name():
    with pytest.raises(ValidationError, match="price must be a number"):
        validate_number("abc", "price")


@pytest.mark.parametrize("value", [0, 5, 0.01])
def test_validate_non_negative_accepts(value):
    assert validate_non_negative(value) == value


@pytest.mark.parametrize("value", [-1, -0.01])
def test_validate_non_negative_rejects(value):
    with pytest.raises(ValidationError, match="cannot be negative"):
        validate_non_negative(value)


@pytest.mark.parametrize("value", [0, -3])
def test_validate_positive_rejects(value):
    with pytest.raises(ValidationError, match="greater than zero"):
        validate_positive(value)


@pytest.mark.parametrize("value", [0, 50, 100, 12.5])
def test_validate_percentage_accepts(value):
    assert validate_percentage(value) == value


@pytest.mark.parametrize("value", [-0.1, 100.1, 200])
def test_validate_percentage_rejects_out_of_range(value):
    with pytest.raises(ValidationError, match="between 0 and 100"):
        validate_percentage(value)


@pytest.mark.parametrize("value", [1, 10, 999])
def test_validate_quantity_accepts(value):
    assert validate_quantity(value) == value


@pytest.mark.parametrize("value", [0, -1, 1.5, "2", True, None])
def test_validate_quantity_rejects(value):
    with pytest.raises(ValidationError):
        validate_quantity(value)


@pytest.mark.parametrize(
    "value, expected", [("PL", "PL"), ("pl", "PL"), (" de ", "DE")]
)
def test_validate_country_code_normalizes(value, expected):
    assert validate_country_code(value) == expected


@pytest.mark.parametrize("value", ["", "POL", "P1", "  ", None, 48])
def test_validate_country_code_rejects(value):
    with pytest.raises(ValidationError, match="country_code"):
        validate_country_code(value)
