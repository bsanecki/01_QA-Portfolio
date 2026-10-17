import pytest

pytestmark = [pytest.mark.smoke]

def test_api_root_resource_is_available(api_client):
    response = api_client.get("/posts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

def test_known_post_is_available(api_client):
    response = api_client.get("/posts/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1
