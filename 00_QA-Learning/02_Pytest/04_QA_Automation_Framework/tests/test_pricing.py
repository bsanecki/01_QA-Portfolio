import dataclasses

import pytest

from app.exceptions import ValidationError
from app.pricing import (
    PriceBreakdown,
    add_tax,
    apply_discount,
    calculate_final_price,
    percent_change,
    percent_of,
    round_money,
)

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "value, expected",
    [(2.675, 2.68), (1.005, 1.01), (10, 10.0), (0.004, 0.0), (-2.675, -2.68)],
)
def test_round_money_rounds_half_up(value, expected):
    assert round_money(value) == expected


@pytest.mark.parametrize(
    "value, percent, expected",
    [(200, 10, 20), (50, 50, 25), (80, 12.5, 10), (100, 0, 0), (100, 150, 150), (-100, 10, -10)],
)
def test_percent_of(value, percent, expected):
    assert percent_of(value, percent) == expected


@pytest.mark.parametrize(
    "old, new, expected",
    [(100, 150, 50), (200, 100, -50), (50, 50, 0), (-100, -50, 50)],
)
def test_percent_change(old, new, expected):
    assert percent_change(old, new) == expected


def test_percent_change_from_zero():
    with pytest.raises(ValueError, match="from zero"):
        percent_change(0, 10)


@pytest.mark.parametrize(
    "price, discount, expected",
    [(100, 0, 100), (100, 10, 90), (100, 100, 0), (59.99, 15, 50.99), (0, 50, 0)],
)
def test_apply_discount(price, discount, expected):
    assert apply_discount(price, discount) == expected


@pytest.mark.parametrize(
    "net, tax, expected",
    [(100, 23, 123), (100, 0, 100), (49.99, 8, 53.99), (0, 23, 0)],
)
def test_add_tax(net, tax, expected):
    assert add_tax(net, tax) == expected


def test_calculate_final_price_full_example():
    result = calculate_final_price(
        unit_price=100, quantity=3, discount_percent=10, tax_percent=23
    )

    assert result == PriceBreakdown(
        unit_price=100,
        quantity=3,
        subtotal=300.0,
        discount_amount=30.0,
        net_total=270.0,
        tax_amount=62.1,
        total=332.1,
    )


def test_calculate_final_price_defaults_mean_no_discount_no_tax():
    result = calculate_final_price(19.99)

    assert result.quantity == 1
    assert result.discount_amount == 0
    assert result.tax_amount == 0
    assert result.total == 19.99


def test_breakdown_is_consistent():
    result = calculate_final_price(33.33, quantity=7, discount_percent=12.5, tax_percent=8)

    assert result.subtotal - result.discount_amount == pytest.approx(result.net_total)
    assert result.net_total + result.tax_amount == pytest.approx(result.total)


def test_breakdown_is_immutable():
    result = calculate_final_price(10)

    with pytest.raises(dataclasses.FrozenInstanceError):
        result.total = 1


@pytest.mark.validation
@pytest.mark.parametrize(
    "kwargs, message",
    [
        ({"unit_price": -1}, "unit_price cannot be negative"),
        ({"unit_price": "10"}, "unit_price must be a number"),
        ({"unit_price": 10, "quantity": 0}, "quantity must be greater than zero"),
        ({"unit_price": 10, "quantity": 1.5}, "quantity must be an integer"),
        ({"unit_price": 10, "discount_percent": 101}, "discount_percent must be between"),
        ({"unit_price": 10, "tax_percent": -5}, "tax_percent must be between"),
    ],
)
def test_calculate_final_price_validation(kwargs, message):
    with pytest.raises(ValidationError, match=message):
        calculate_final_price(**kwargs)


@pytest.mark.validation
@pytest.mark.parametrize("func", [percent_of, percent_change])
def test_percent_functions_reject_non_numbers(func):
    with pytest.raises(ValidationError):
        func("10", 5)
