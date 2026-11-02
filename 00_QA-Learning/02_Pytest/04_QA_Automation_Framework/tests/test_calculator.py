import pytest

from app.calculator import (
    add, subtract, multiply, divide, power, square_root, average,
)
from app.exceptions import ValidationError

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "a, b, expected",
    [(2, 3, 5), (10, 5, 15), (-5, 5, 0), (0, 10, 10), (2.5, 2.5, 5)],
)
def test_add(a, b, expected):
    assert add(a, b) == expected


@pytest.mark.parametrize(
    "a, b, expected",
    [(10, 5, 5), (5, 10, -5), (0, 5, -5), (100, 25, 75), (2.5, 1, 1.5)],
)
def test_subtract(a, b, expected):
    assert subtract(a, b) == expected


@pytest.mark.parametrize(
    "a, b, expected",
    [(2, 3, 6), (10, 5, 50), (-5, 5, -25), (0, 100, 0), (2.5, 4, 10)],
)
def test_multiply(a, b, expected):
    assert multiply(a, b) == expected


@pytest.mark.parametrize(
    "a, b, expected",
    [(10, 2, 5), (100, 4, 25), (5, 2, 2.5), (0, 10, 0)],
)
def test_divide(a, b, expected):
    assert divide(a, b) == expected


def test_divide_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)


@pytest.mark.parametrize(
    "base, exponent, expected",
    [(2, 3, 8), (5, 0, 1), (4, 0.5, 2), (2, -1, 0.5), (0, 5, 0)],
)
def test_power(base, exponent, expected):
    assert power(base, exponent) == expected


def test_power_zero_to_negative_exponent():
    with pytest.raises(ValueError, match="negative power"):
        power(0, -1)


def test_power_complex_result_is_rejected():
    with pytest.raises(ValueError, match="not a real number"):
        power(-8, 0.5)


@pytest.mark.parametrize("value, expected", [(0, 0), (9, 3), (2.25, 1.5)])
def test_square_root(value, expected):
    assert square_root(value) == pytest.approx(expected)


def test_square_root_of_negative_number():
    with pytest.raises(ValueError, match="negative"):
        square_root(-4)


def test_average():
    assert average([1, 2, 3, 4]) == 2.5
    assert average((10,)) == 10


def test_average_of_empty_list():
    with pytest.raises(ValueError, match="empty"):
        average([])


def test_average_rejects_non_iterable():
    with pytest.raises(TypeError):
        average(5)


def test_average_rejects_invalid_element():
    with pytest.raises(ValidationError, match=r"numbers\[1\]"):
        average([1, "2", 3])


def test_float_results_need_approx():

    assert add(0.1, 0.2) != 0.3
    assert add(0.1, 0.2) == pytest.approx(0.3)


@pytest.mark.validation
@pytest.mark.parametrize("func", [add, subtract, multiply, divide, power])
@pytest.mark.parametrize("bad", ["5", None, True, [1], float("nan"), float("inf")])
def test_binary_operations_reject_invalid_input(func, bad):
    with pytest.raises(ValidationError):
        func(bad, 1)
    with pytest.raises(ValidationError):
        func(1, bad)
