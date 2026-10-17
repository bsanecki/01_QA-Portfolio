import pytest
pytestmark = [pytest.mark.contract, pytest.mark.headers]

@pytest.mark.parametrize("path", ["/posts", "/users", "/comments", "/todos", "/albums", "/photos"])
def test_resources_return_success_status(api_client, path):
    assert api_client.get(path).status_code == 200

@pytest.mark.parametrize("path", ["/posts/1", "/users/1", "/comments/1", "/todos/1", "/albums/1", "/photos/1"])
def test_single_resource_returns_json_object(api_client, path):
    r = api_client.get(path)
    assert r.status_code == 200
    assert isinstance(r.json(), dict)

def test_content_type_is_json(api_client):
    response = api_client.get("/posts/1")
    assert "application/json" in response.headers.get("Content-Type", "")

def test_accept_json_header_is_supported(api_client):
    response = api_client.get("/posts/1", headers={"Accept": "application/json"})
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_response_contains_content_type_header(api_client):
    assert "Content-Type" in api_client.get("/posts").headers

def test_response_has_status_code_attribute(api_client):
    assert isinstance(api_client.get("/posts").status_code, int)
