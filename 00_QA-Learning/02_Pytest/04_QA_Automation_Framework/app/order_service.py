from app.exceptions import TaxRateUnavailableError
from app.pricing import PriceBreakdown, calculate_final_price, round_money
from app.validators import validate_country_code


class OrderService:
    def __init__(self, tax_provider, history):
        self.tax_provider = tax_provider
        self.history = history

    def _get_tax_rate(self, country_code):
        country_code = validate_country_code(country_code)

        try:
            rate = self.tax_provider.get_tax_rate(country_code)
        except ConnectionError as error:
            raise TaxRateUnavailableError(
                f"Tax service unavailable for {country_code}."
            ) from error

        if rate is None:
            raise TaxRateUnavailableError(f"No tax rate for {country_code}.")

        return rate

    def calculate_order(self, unit_price, quantity, country_code, discount_percent=0):
        tax_rate = self._get_tax_rate(country_code)

        breakdown = calculate_final_price(
            unit_price,
            quantity=quantity,
            discount_percent=discount_percent,
            tax_percent=tax_rate,
        )

        self.history.add(
            "order",
            {
                "unit_price": unit_price,
                "quantity": quantity,
                "country_code": country_code.strip().upper(),
                "discount_percent": discount_percent,
                "tax_rate": tax_rate,
            },
            breakdown.total,
        )

        return breakdown

    def calculate_cart(self, items, country_code, discount_percent=0):
        if not items:
            raise ValueError("Cart cannot be empty.")

        breakdowns = [
            self.calculate_order(
                item["unit_price"], item["quantity"], country_code, discount_percent
            )
            for item in items
        ]

        return PriceBreakdown(
            unit_price=0,
            quantity=sum(b.quantity for b in breakdowns),
            subtotal=round_money(sum(b.subtotal for b in breakdowns)),
            discount_amount=round_money(sum(b.discount_amount for b in breakdowns)),
            net_total=round_money(sum(b.net_total for b in breakdowns)),
            tax_amount=round_money(sum(b.tax_amount for b in breakdowns)),
            total=round_money(sum(b.total for b in breakdowns)),
        )
