import pytest
pytestmark = [pytest.mark.comments]

def test_get_comments_returns_list(api_client):
    r = api_client.get("/comments"); assert r.status_code == 200; assert isinstance(r.json(), list)

def test_comments_collection_has_500_items(api_client):
    assert len(api_client.get("/comments").json()) == 500

def test_single_comment_has_expected_fields(api_client):
    comment = api_client.get("/comments/1").json()
    assert {"postId", "id", "name", "email", "body"}.issubset(comment)

def test_comment_field_types(api_client):
    comment = api_client.get("/comments/1").json()
    assert isinstance(comment["postId"], int); assert isinstance(comment["id"], int)
    assert isinstance(comment["name"], str); assert isinstance(comment["email"], str); assert isinstance(comment["body"], str)

def test_comment_email_contains_at_symbol(api_client):
    assert "@" in api_client.get("/comments/1").json()["email"]
