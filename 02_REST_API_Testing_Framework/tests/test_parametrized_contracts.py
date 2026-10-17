import json
from pathlib import Path

import allure
import pytest
from jsonschema import Draft202012Validator, FormatChecker

pytestmark = [pytest.mark.contract]
SCHEMA_DIR = Path(__file__).resolve().parents[1] / "schemas"


def read_schema(name):
    with (SCHEMA_DIR / name).open(encoding="utf-8") as file:
        return json.load(file)


def attach_exchange(response, name):
    request_data = {
        "method": response.request.method,
        "url": response.request.url,
        "headers": dict(response.request.headers),
        "body": response.request.body.decode("utf-8", errors="replace")
        if isinstance(response.request.body, bytes)
        else response.request.body,
    }
    response_data = {
        "status_code": response.status_code,
        "headers": dict(response.headers),
        "body": response.text,
    }
    allure.attach(
        json.dumps(request_data, indent=2, default=str),
        name=f"{name}-request.json",
        attachment_type=allure.attachment_type.JSON,
    )
    allure.attach(
        json.dumps(response_data, indent=2, default=str),
        name=f"{name}-response.json",
        attachment_type=allure.attachment_type.JSON,
    )


@pytest.mark.parametrize(
    ("resource", "resource_id", "expected_schema"),
    [
        pytest.param("posts", 1, "post.schema.json", id="post-valid-id"),
        pytest.param("posts", 100, "post.schema.json", id="post-last-id"),
        pytest.param("users", 1, "user.schema.json", id="user-valid-id"),
        pytest.param("comments", 1, "comment.schema.json", id="comment-valid-id"),
        pytest.param("todos", 1, "todo.schema.json", id="todo-valid-id"),
    ],
)
@allure.epic("REST API")
@allure.feature("Response contracts")
@allure.story("Single resource schema validation")
@allure.severity(allure.severity_level.CRITICAL)
def test_resource_response_matches_contract(api_client, resource, resource_id, expected_schema):
    with allure.step(f"Send GET /{resource}/{resource_id}"):
        response = api_client.get(f"/{resource}/{resource_id}")
        attach_exchange(response, f"{resource}-{resource_id}")
        assert response.status_code == 200
        payload = response.json()

    with allure.step(f"Validate {resource} response schema"):
        validator = Draft202012Validator(
            read_schema(expected_schema), format_checker=FormatChecker()
        )
        errors = sorted(validator.iter_errors(payload), key=lambda error: list(map(str, error.path)))
        assert not errors, "\n".join(
            f"{list(error.path) or '<root>'}: {error.message}" for error in errors
        )


@pytest.mark.parametrize(
    ("resource", "query_value", "expected_status"),
    [
        pytest.param("posts", "1", 200, id="numeric-id"),
        pytest.param("posts", "abc", 200, id="text-id-filter"),
        pytest.param("posts", "", 200, id="empty-id-filter"),
        pytest.param("posts", "-1", 200, id="negative-id-filter"),
        pytest.param("posts", "0", 200, id="zero-id-filter"),
    ],
)
@allure.epic("REST API")
@allure.feature("Input validation")
@allure.story("Parameterized query values")
@allure.severity(allure.severity_level.NORMAL)
def test_query_values_are_handled_consistently(api_client, resource, query_value, expected_status):
    with allure.step(f"Send GET /{resource}?userId={query_value!r}"):
        response = api_client.get(f"/{resource}", params={"userId": query_value})
        attach_exchange(response, f"{resource}-userId-{query_value or 'empty'}")
        assert response.status_code == expected_status
        assert isinstance(response.json(), list)


@pytest.mark.parametrize(
    ("payload", "case_name"),
    [
        pytest.param({"userId": 1, "id": 1, "title": "Valid", "body": "Valid"}, "valid", id="valid-payload"),
        pytest.param({"title": 123, "body": "Valid", "userId": 1}, "title-number", id="wrong-title-type"),
        pytest.param({"title": "Valid", "body": None, "userId": 1}, "body-null", id="null-body"),
        pytest.param({"title": "Valid", "body": "Valid", "userId": "1"}, "userid-string", id="string-user-id"),
        pytest.param({"title": "Valid", "body": "Valid"}, "missing-userid", id="missing-required-field"),
        pytest.param({"title": "Valid", "body": "Valid", "userId": 1, "extra": True}, "extra-field", id="unexpected-field"),
    ],
)
@allure.epic("REST API")
@allure.feature("Contract validation")
@allure.story("Schema rejects invalid payloads")
@allure.severity(allure.severity_level.NORMAL)
def test_post_schema_accepts_only_contract_payloads(payload, case_name):
    validator = Draft202012Validator(read_schema("post.schema.json"), format_checker=FormatChecker())
    errors = list(validator.iter_errors(payload))
    if case_name == "valid":
        assert not errors
    else:
        assert errors, f"Invalid payload unexpectedly passed: {case_name}"
