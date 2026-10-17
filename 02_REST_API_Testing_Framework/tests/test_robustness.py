import pytest
from config.settings import MAX_RESPONSE_TIME_SECONDS
pytestmark = [pytest.mark.robustness]

@pytest.mark.parametrize("path", ["/posts", "/users", "/comments", "/todos", "/albums", "/photos"])
def test_common_endpoints_respond_within_time_limit(api_client, path):
    response = api_client.get(path)
    assert response.status_code == 200
    assert response.elapsed.total_seconds() < MAX_RESPONSE_TIME_SECONDS

def test_repeated_get_requests_remain_successful(api_client):
    statuses = [api_client.get("/posts/1").status_code for _ in range(5)]
    assert statuses == [200] * 5

def test_response_body_is_not_empty(api_client):
    response = api_client.get("/posts/1")
    assert response.content

def test_json_can_be_decoded_repeatedly(api_client):
    response = api_client.get("/users/1")
    assert isinstance(response.json(), dict)
    assert isinstance(response.json(), dict)
