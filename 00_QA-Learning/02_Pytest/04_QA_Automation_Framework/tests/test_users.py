import pytest

pytestmark = pytest.mark.service


def test_get_user(seeded_user_service, sample_user):
    assert seeded_user_service.get_user(1) == sample_user


def test_get_user_name(seeded_user_service):
    assert seeded_user_service.get_user_name(1) == "Anna"


def test_active_user(seeded_user_service):
    assert seeded_user_service.is_active(1) is True


def test_inactive_user(seeded_user_service):
    assert seeded_user_service.is_active(2) is False


def test_missing_user(seeded_user_service):
    with pytest.raises(LookupError, match="User not found"):
        seeded_user_service.get_user(999)


@pytest.mark.parametrize(
    "name, email",
    [
        ("Jan", "jan@example.com"),
        ("Anna", "anna@example.com"),
        ("Piotr", "piotr@test.com"),
    ],
)
def test_create_user(user_service, mock_user_api, name, email):
    expected = {"id": 10, "name": name, "email": email, "status": "active"}
    mock_user_api.create_user.return_value = expected

    result = user_service.create_user(name, email)

    assert result == expected
    mock_user_api.create_user.assert_called_once_with(
        {"name": name, "email": email, "status": "active"}
    )


@pytest.mark.validation
@pytest.mark.parametrize(
    "name, email, message",
    [
        ("", "jan@example.com", "Name cannot be empty"),
        ("   ", "jan@example.com", "Name cannot be empty"),
        ("Jan", "invalid-email", "Invalid email"),
    ],
)
def test_create_user_validation(user_service, mock_user_api, name, email, message):
    with pytest.raises(ValueError, match=message):
        user_service.create_user(name, email)

    mock_user_api.create_user.assert_not_called()
