import pytest

from app.exceptions import TaxRateUnavailableError, ValidationError
from app.history import CalculationHistory
from app.order_service import OrderService
from app.tax_provider import StaticTaxRateProvider

pytestmark = pytest.mark.service


def test_calculate_order_uses_tax_rate_from_provider(order_service, mock_tax_provider):
    result = order_service.calculate_order(100, 2, "PL", discount_percent=10)

    assert result.subtotal == 200
    assert result.net_total == 180
    assert result.total == 221.4
    mock_tax_provider.get_tax_rate.assert_called_once_with("PL")


def test_country_code_is_normalized_before_calling_provider(order_service, mock_tax_provider):
    order_service.calculate_order(10, 1, " pl ")

    mock_tax_provider.get_tax_rate.assert_called_once_with("PL")


@pytest.mark.parametrize(
    "rate, expected_total", [(0, 100), (8, 108), (19, 119), (23, 123)]
)
def test_different_tax_rates(order_service, mock_tax_provider, rate, expected_total):
    mock_tax_provider.get_tax_rate.return_value = rate

    assert order_service.calculate_order(100, 1, "XX").total == expected_total


def test_order_is_saved_in_history(order_service, history):
    result = order_service.calculate_order(50, 2, "pl")

    entry = history.last()
    assert entry.operation == "order"
    assert entry.result == result.total
    assert entry.inputs["country_code"] == "PL"
    assert entry.inputs["tax_rate"] == 23


def test_provider_connection_error_becomes_domain_error(order_service, mock_tax_provider):
    mock_tax_provider.get_tax_rate.side_effect = ConnectionError("timeout")

    with pytest.raises(TaxRateUnavailableError, match="unavailable") as exc_info:
        order_service.calculate_order(100, 1, "PL")

    assert isinstance(exc_info.value.__cause__, ConnectionError)


def test_unknown_country_raises(order_service, mock_tax_provider):
    mock_tax_provider.get_tax_rate.return_value = None

    with pytest.raises(TaxRateUnavailableError, match="No tax rate"):
        order_service.calculate_order(100, 1, "ZZ")


def test_failed_order_is_not_saved_in_history(order_service, mock_tax_provider, history):
    mock_tax_provider.get_tax_rate.side_effect = ConnectionError()

    with pytest.raises(TaxRateUnavailableError):
        order_service.calculate_order(100, 1, "PL")

    assert len(history) == 0


@pytest.mark.validation
def test_invalid_input_does_not_call_provider_for_bad_country(order_service, mock_tax_provider):
    with pytest.raises(ValidationError, match="country_code"):
        order_service.calculate_order(100, 1, "POLAND")

    mock_tax_provider.get_tax_rate.assert_not_called()


@pytest.mark.validation
@pytest.mark.parametrize(
    "price, quantity, discount",
    [(-1, 1, 0), (10, 0, 0), (10, 1, 150), ("10", 1, 0)],
)
def test_invalid_order_data_is_rejected_and_not_saved(order_service, history, price, quantity, discount):
    with pytest.raises(ValidationError):
        order_service.calculate_order(price, quantity, "PL", discount)

    assert len(history) == 0


def test_cart_sums_all_items(order_service, mock_tax_provider, history):
    items = [
        {"unit_price": 10, "quantity": 2},
        {"unit_price": 5.5, "quantity": 1},
    ]

    result = order_service.calculate_cart(items, "PL")

    assert result.quantity == 3
    assert result.subtotal == 25.5
    assert result.total == 31.37
    assert mock_tax_provider.get_tax_rate.call_count == 2
    assert len(history) == 2


@pytest.mark.parametrize("items", [[], None])
def test_empty_cart_is_rejected(order_service, items):
    with pytest.raises(ValueError, match="Cart cannot be empty"):
        order_service.calculate_cart(items, "PL")


def test_with_real_static_provider_no_mock(fixed_time):
    service = OrderService(
        StaticTaxRateProvider(), CalculationHistory(clock=lambda: fixed_time)
    )

    assert service.calculate_order(100, 1, "DE").total == 119
    assert service.calculate_order(100, 1, "US").total == 100
    with pytest.raises(TaxRateUnavailableError):
        service.calculate_order(100, 1, "JP")
