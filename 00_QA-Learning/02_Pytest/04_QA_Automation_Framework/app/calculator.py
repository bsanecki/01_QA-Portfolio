import math

from app.validators import validate_number


def add(a, b):
    validate_number(a, "a")
    validate_number(b, "b")
    return a + b


def subtract(a, b):
    validate_number(a, "a")
    validate_number(b, "b")
    return a - b


def multiply(a, b):
    validate_number(a, "a")
    validate_number(b, "b")
    return a * b


def divide(a, b):
    validate_number(a, "a")
    validate_number(b, "b")

    if b == 0:
        raise ValueError("Cannot divide by zero.")

    return a / b


def power(base, exponent):
    validate_number(base, "base")
    validate_number(exponent, "exponent")

    if base == 0 and exponent < 0:
        raise ValueError("Cannot raise zero to a negative power.")

    result = base ** exponent

    if isinstance(result, complex):
        raise ValueError("Result is not a real number.")

    return result


def square_root(value):
    validate_number(value, "value")

    if value < 0:
        raise ValueError("Cannot take square root of a negative number.")

    return math.sqrt(value)


def average(numbers):
    if isinstance(numbers, (str, bytes)) or not hasattr(numbers, "__iter__"):
        raise TypeError("numbers must be a list or other iterable of numbers.")

    numbers = list(numbers)

    if not numbers:
        raise ValueError("Cannot calculate average of an empty list.")

    for index, number in enumerate(numbers):
        validate_number(number, f"numbers[{index}]")

    return sum(numbers) / len(numbers)
