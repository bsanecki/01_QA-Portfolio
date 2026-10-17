
import allure
import pytest

pytestmark = [pytest.mark.edge_cases, pytest.mark.negative, pytest.mark.robustness]


@pytest.mark.parametrize("resource", ["posts", "users", "comments", "todos"])
@pytest.mark.parametrize("resource_id", [0, -1, 999999])
def test_out_of_range_resource_ids_do_not_return_successful_resource(api_client, resource, resource_id):
    with allure.step(f"Request /{resource}/{resource_id}"):
        response = api_client.get(f"/{resource}/{resource_id}")
    
    assert response.status_code == 404


@pytest.mark.parametrize("value", ["", "   ", "abc", "1.5", "-1", "999999999999999999999999"])
def test_unusual_user_id_filter_does_not_cause_server_error(api_client, value):
    with allure.step(f"GET /posts?userId={value!r}"):
        response = api_client.get("/posts", params={"userId": value})
    assert response.status_code < 500
    assert isinstance(response.json(), list)


def test_unknown_query_parameter_is_ignored_safely(api_client):
    response = api_client.get("/posts", params={"qa_unknown_filter": "anything"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_long_query_value_does_not_cause_server_error(api_client):
    response = api_client.get("/posts", params={"title": "x" * 2000})
    assert response.status_code < 500
    assert isinstance(response.json(), list)


def test_special_characters_in_query_are_handled(api_client):
    response = api_client.get("/posts", params={"title": "<script>alert('qa')</script> & ? # %"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_accept_header_for_json_is_supported(api_client):
    response = api_client.get("/posts/1", headers={"Accept": "application/json"})
    assert response.status_code == 200
    assert response.headers.get("Content-Type", "").startswith("application/json")


def test_unacceptable_accept_header_is_handled_without_server_error(api_client):
    response = api_client.get("/posts/1", headers={"Accept": "application/xml"})
    assert response.status_code < 500
