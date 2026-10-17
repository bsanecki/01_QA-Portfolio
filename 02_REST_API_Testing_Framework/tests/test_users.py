import pytest
pytestmark = [pytest.mark.users]

def test_get_all_users_returns_list(api_client):
    r = api_client.get("/users"); assert r.status_code == 200; assert isinstance(r.json(), list)

def test_users_collection_has_10_items(api_client):
    assert len(api_client.get("/users").json()) == 10

@pytest.mark.parametrize("user_id", range(1, 11))
def test_known_user_ids_return_matching_id(api_client, user_id):
    r = api_client.get(f"/users/{user_id}"); assert r.status_code == 200; assert r.json()["id"] == user_id

def test_user_required_fields(api_client):
    user = api_client.get("/users/1").json()
    assert {"id", "name", "username", "email", "address", "phone", "website", "company"}.issubset(user)

def test_user_field_types(api_client):
    user = api_client.get("/users/1").json()
    assert isinstance(user["id"], int); assert isinstance(user["name"], str)
    assert isinstance(user["username"], str); assert isinstance(user["email"], str)

def test_user_email_contains_at_symbol(api_client):
    email = api_client.get("/users/1").json()["email"]
    assert "@" in email

def test_user_address_has_city_and_street(api_client):
    address = api_client.get("/users/1").json()["address"]
    assert address["city"]; assert address["street"]
