from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from app.validators import (
    validate_non_negative,
    validate_number,
    validate_percentage,
    validate_quantity,
)


def round_money(value):
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def percent_of(value, percent):
    validate_number(value, "value")
    validate_number(percent, "percent")
    return round_money(value * percent / 100)


def percent_change(old, new):
    validate_number(old, "old")
    validate_number(new, "new")

    if old == 0:
        raise ValueError("Cannot calculate percent change from zero.")

    return round_money((new - old) / abs(old) * 100)


def apply_discount(price, discount_percent):
    validate_non_negative(price, "price")
    validate_percentage(discount_percent, "discount_percent")
    return round_money(price * (100 - discount_percent) / 100)


def add_tax(net_price, tax_percent):
    validate_non_negative(net_price, "net_price")
    validate_percentage(tax_percent, "tax_percent")
    return round_money(net_price * (100 + tax_percent) / 100)


@dataclass(frozen=True)
class PriceBreakdown:
    unit_price: float
    quantity: int
    subtotal: float
    discount_amount: float
    net_total: float
    tax_amount: float
    total: float


def calculate_final_price(unit_price, quantity=1, discount_percent=0, tax_percent=0):
    validate_non_negative(unit_price, "unit_price")
    validate_quantity(quantity)
    validate_percentage(discount_percent, "discount_percent")
    validate_percentage(tax_percent, "tax_percent")

    subtotal = round_money(unit_price * quantity)
    net_total = apply_discount(subtotal, discount_percent)
    total = add_tax(net_total, tax_percent)

    return PriceBreakdown(
        unit_price=unit_price,
        quantity=quantity,
        subtotal=subtotal,
        discount_amount=round_money(subtotal - net_total),
        net_total=net_total,
        tax_amount=round_money(total - net_total),
        total=total,
    )
