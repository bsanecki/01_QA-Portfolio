import pytest
pytestmark = [pytest.mark.crud]

def test_create_post_returns_created_representation(api_client, valid_post_payload):
    r = api_client.post("/posts", json=valid_post_payload)
    assert r.status_code == 201
    body = r.json()
    assert body["title"] == valid_post_payload["title"]
    assert body["body"] == valid_post_payload["body"]
    assert body["userId"] == valid_post_payload["userId"]
    assert "id" in body

def test_replace_post_with_put(api_client):
    payload = {"id": 1, "title": "Updated title", "body": "Updated body", "userId": 1}
    r = api_client.put("/posts/1", json=payload)
    assert r.status_code == 200; assert r.json()["title"] == payload["title"]

def test_update_post_field_with_patch(api_client):
    r = api_client.patch("/posts/1", json={"title": "Patched title"})
    assert r.status_code == 200; assert r.json()["title"] == "Patched title"

def test_delete_post_returns_success_status(api_client):
    r = api_client.delete("/posts/1")
    assert r.status_code in (200, 204)

def test_create_todo_returns_created_representation(api_client, valid_todo_payload):
    r = api_client.post("/todos", json=valid_todo_payload)
    assert r.status_code == 201
    assert r.json()["title"] == valid_todo_payload["title"]
    assert r.json()["completed"] is False

