import pytest
pytestmark = [pytest.mark.todos]

def test_get_todos_returns_list(api_client):
    r = api_client.get("/todos"); assert r.status_code == 200; assert isinstance(r.json(), list)

def test_todos_collection_has_200_items(api_client):
    assert len(api_client.get("/todos").json()) == 200

def test_single_todo_has_expected_fields(api_client):
    todo = api_client.get("/todos/1").json()
    assert {"userId", "id", "title", "completed"}.issubset(todo)

def test_todo_field_types(api_client):
    todo = api_client.get("/todos/1").json()
    assert isinstance(todo["userId"], int); assert isinstance(todo["id"], int)
    assert isinstance(todo["title"], str); assert isinstance(todo["completed"], bool)

def test_completed_filter_returns_matching_todos(api_client):
    r = api_client.get("/todos", params={"completed": "true"})
    assert r.status_code == 200
    assert all(todo["completed"] is True for todo in r.json())
