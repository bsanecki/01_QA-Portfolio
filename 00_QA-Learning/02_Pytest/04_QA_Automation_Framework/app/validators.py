import math
from numbers import Real

from app.exceptions import ValidationError


def validate_number(value, name="value"):
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValidationError(f"{name} must be a number.")

    if math.isnan(value) or math.isinf(value):
        raise ValidationError(f"{name} must be a finite number.")

    return value


def validate_non_negative(value, name="value"):
    validate_number(value, name)

    if value < 0:
        raise ValidationError(f"{name} cannot be negative.")

    return value


def validate_positive(value, name="value"):
    validate_number(value, name)

    if value <= 0:
        raise ValidationError(f"{name} must be greater than zero.")

    return value


def validate_percentage(value, name="percent"):
    validate_number(value, name)

    if not 0 <= value <= 100:
        raise ValidationError(f"{name} must be between 0 and 100.")

    return value


def validate_quantity(value, name="quantity"):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError(f"{name} must be an integer.")

    if value <= 0:
        raise ValidationError(f"{name} must be greater than zero.")

    return value


def validate_country_code(value):
    if not isinstance(value, str) or len(value.strip()) != 2 or not value.strip().isalpha():
        raise ValidationError("country_code must be a 2-letter code.")

    return value.strip().upper()
