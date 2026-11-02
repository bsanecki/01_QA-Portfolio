import pytest

pytestmark = pytest.mark.service


def test_get_user_calls_api_once(user_service, mock_user_api):
    mock_user_api.get_user.return_value = {"id": 1, "name": "Anna", "status": "active"}

    result = user_service.get_user(1)

    assert result["id"] == 1
    mock_user_api.get_user.assert_called_once_with(1)


def test_api_response_is_used(user_service, mock_user_api):
    mock_user_api.get_user.return_value = {
        "id": 5,
        "name": "Test User",
        "email": "test@example.com",
        "status": "active",
    }

    assert user_service.get_user_name(5) == "Test User"
    mock_user_api.get_user.assert_called_once_with(5)


def test_api_returning_none_means_user_not_found(user_service, mock_user_api):
    mock_user_api.get_user.return_value = None

    with pytest.raises(LookupError, match="User not found"):
        user_service.get_user(50)


def test_api_exception_is_propagated(user_service, mock_user_api):
    mock_user_api.get_user.side_effect = ConnectionError("API down")

    with pytest.raises(ConnectionError, match="API down"):
        user_service.get_user(1)


def test_create_user_uses_api(user_service, mock_user_api):
    mock_user_api.create_user.return_value = {
        "id": 20,
        "name": "New User",
        "email": "new@example.com",
        "status": "active",
    }

    result = user_service.create_user("New User", "new@example.com")

    assert result["status"] == "active"
    mock_user_api.create_user.assert_called_once()


def test_mock_can_return_different_users(user_service, mock_user_api):
    mock_user_api.get_user.side_effect = [
        {"id": 1, "name": "Anna", "status": "active"},
        {"id": 2, "name": "Jan", "status": "inactive"},
    ]

    assert user_service.get_user_name(1) == "Anna"
    assert user_service.get_user_name(2) == "Jan"
    assert mock_user_api.get_user.call_count == 2


def test_autospec_rejects_methods_missing_in_the_real_api(mock_user_api):
    with pytest.raises(AttributeError):
        mock_user_api.delete_user(1)
