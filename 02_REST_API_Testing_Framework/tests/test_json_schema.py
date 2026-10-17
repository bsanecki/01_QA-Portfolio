
import json
from pathlib import Path

import allure
import pytest
from jsonschema import Draft202012Validator, FormatChecker

pytestmark = [pytest.mark.contract]
SCHEMA_DIR = Path(__file__).resolve().parents[1] / "schemas"


def load_schema(filename):
    with (SCHEMA_DIR / filename).open(encoding="utf-8") as file:
        return json.load(file)


@pytest.mark.parametrize(
    ("resource", "resource_id", "schema_file"),
    [
        ("posts", 1, "post.schema.json"),
        ("users", 1, "user.schema.json"),
        ("comments", 1, "comment.schema.json"),
        ("todos", 1, "todo.schema.json"),
    ],
)
def test_resource_matches_json_schema(api_client, resource, resource_id, schema_file):
    with allure.step(f"GET /{resource}/{resource_id}"):
        response = api_client.get(f"/{resource}/{resource_id}")
        assert response.status_code == 200
        payload = response.json()
        allure.attach(
            json.dumps(payload, indent=2),
            name=f"{resource}-response.json",
            attachment_type=allure.attachment_type.JSON,
        )

    with allure.step(f"Validate response against {schema_file}"):
        validator = Draft202012Validator(load_schema(schema_file), format_checker=FormatChecker())
        errors = sorted(validator.iter_errors(payload), key=lambda error: list(map(str, error.path)))
        assert not errors, "\n".join(
            f"{list(error.path) or '<root>'}: {error.message}" for error in errors
        )


@pytest.mark.parametrize(
    ("resource", "schema_file"),
    [("posts", "post.schema.json"), ("users", "user.schema.json"),
     ("comments", "comment.schema.json"), ("todos", "todo.schema.json")],
)
def test_every_item_in_collection_matches_schema(api_client, resource, schema_file):
    response = api_client.get(f"/{resource}")
    assert response.status_code == 200
    validator = Draft202012Validator(load_schema(schema_file), format_checker=FormatChecker())
    errors = []
    for index, item in enumerate(response.json()):
        for error in validator.iter_errors(item):
            errors.append(f"item[{index}] {list(error.path)}: {error.message}")
    assert not errors, "\n".join(errors[:30])
