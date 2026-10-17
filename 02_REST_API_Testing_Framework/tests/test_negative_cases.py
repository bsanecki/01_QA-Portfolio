import pytest
pytestmark = [pytest.mark.negative]

@pytest.mark.parametrize("resource", ["posts", "users", "comments", "todos", "albums", "photos"])
def test_unknown_numeric_resource_id_returns_not_found(api_client, resource):
    response = api_client.get(f"/{resource}/999999")
    assert response.status_code == 404

def test_unknown_route_returns_not_found(api_client):
    assert api_client.get("/this-route-should-not-exist").status_code == 404

@pytest.mark.parametrize("resource", ["posts", "users", "comments", "todos", "albums", "photos"])
def test_nonnumeric_id_is_handled_without_server_error(api_client, resource):
    response = api_client.get(f"/{resource}/not-a-number")
    assert response.status_code < 500

@pytest.mark.parametrize("user_id", ["abc", "0", "-1"])
def test_invalid_user_id_filter_does_not_cause_server_error(api_client, user_id):
    response = api_client.get("/posts", params={"userId": user_id})
    assert response.status_code < 500
    assert isinstance(response.json(), list)

def test_empty_query_filter_is_handled(api_client):
    response = api_client.get("/posts", params={"userId": ""})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_unusual_query_text_does_not_cause_server_error(api_client):
    response = api_client.get("/posts", params={"userId": "<script>alert(1)</script>"})
    assert response.status_code < 500
