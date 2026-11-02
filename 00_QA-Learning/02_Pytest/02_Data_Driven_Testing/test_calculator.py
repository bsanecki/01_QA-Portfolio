import pytest

from calculator import (
    add,
    subtract,
    multiply,
    divide,
    calculate_discount,
    calculate_tax,
    calculate_final_price,
)


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (10, 5, 15),
        (100, 25, 125),
        (-10, 5, -5),
        (0, 50, 50),
        (2.5, 2.5, 5),
    ],
)
def test_add(a, b, expected):
    assert add(a, b) == expected


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (10, 5, 5),
        (100, 25, 75),
        (5, 10, -5),
        (0, 50, -50),
        (10.5, 0.5, 10),
    ],
)
def test_subtract(a, b, expected):
    assert subtract(a, b) == expected


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (10, 5, 50),
        (100, 2, 200),
        (-10, 5, -50),
        (0, 100, 0),
        (2.5, 4, 10),
    ],
)
def test_multiply(a, b, expected):
    assert multiply(a, b) == expected


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (10, 2, 5),
        (100, 4, 25),
        (9, 3, 3),
        (5, 2, 2.5),
        (0, 10, 0),
    ],
)
def test_divide(a, b, expected):
    assert divide(a, b) == expected


def test_divide_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)


@pytest.mark.parametrize(
    "price, discount, expected",
    [
        (100, 10, 90),
        (200, 20, 160),
        (500, 50, 250),
        (100, 0, 100),
        (80, 25, 60),
        (1000, 15, 850),
    ],
)
def test_calculate_discount(price, discount, expected):
    assert calculate_discount(price, discount) == expected


@pytest.mark.parametrize(
    "price, discount",
    [
        (-100, 10),
        (100, -10),
        (100, 101),
        (500, 150),
    ],
)
def test_invalid_discount_data(price, discount):
    with pytest.raises(ValueError):
        calculate_discount(price, discount)


@pytest.mark.parametrize(
    "price, tax_rate, expected",
    [
        (100, 23, 123),
        (200, 10, 220),
        (500, 0, 500),
        (1000, 20, 1200),
        (80, 5, 84),
    ],
)
def test_calculate_tax(price, tax_rate, expected):
    assert calculate_tax(price, tax_rate) == expected


@pytest.mark.parametrize(
    "price, discount, tax_rate, expected",
    [
        (100, 10, 23, 110.7),
        (200, 20, 23, 196.8),
        (500, 50, 23, 307.5),
        (100, 0, 23, 123),
        (1000, 10, 0, 900),
    ],
)
def test_calculate_final_price(price, discount, tax_rate, expected):
    assert calculate_final_price(
        price,
        discount,
        tax_rate
    ) == expected


@pytest.mark.parametrize(
    "price, discount, tax_rate",
    [
        (-100, 10, 23),
        (100, -10, 23),
        (100, 110, 23),
        (100, 10, -5),
    ],
)
def test_invalid_final_price_data(price, discount, tax_rate):
    with pytest.raises(ValueError):
        calculate_final_price(price, discount, tax_rate)