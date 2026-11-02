from datetime import datetime
from unittest.mock import create_autospec

import pytest

from app.history import CalculationHistory
from app.order_service import OrderService
from app.tax_provider import TaxRateProvider
from app.user_api import UserApi
from app.user_service import UserService


@pytest.fixture
def sample_user():
    return {"id": 1, "name": "Anna", "email": "anna@example.com", "status": "active"}


@pytest.fixture
def inactive_user():
    return {"id": 2, "name": "Jan", "email": "jan@example.com", "status": "inactive"}


@pytest.fixture
def mock_user_api():
    return create_autospec(UserApi, instance=True)


@pytest.fixture
def user_service(mock_user_api):
    return UserService(mock_user_api)


@pytest.fixture
def seeded_user_api(mock_user_api, sample_user, inactive_user):
    users = {1: sample_user, 2: inactive_user}
    mock_user_api.get_user.side_effect = users.get
    return mock_user_api


@pytest.fixture
def seeded_user_service(seeded_user_api):
    return UserService(seeded_user_api)


@pytest.fixture
def fixed_time():
    return datetime(2026, 1, 1, 12, 0, 0)


@pytest.fixture
def history(fixed_time):
    return CalculationHistory(clock=lambda: fixed_time)


@pytest.fixture
def mock_tax_provider():
    provider = create_autospec(TaxRateProvider, instance=True)
    provider.get_tax_rate.return_value = 23
    return provider


@pytest.fixture
def order_service(mock_tax_provider, history):
    return OrderService(mock_tax_provider, history)
