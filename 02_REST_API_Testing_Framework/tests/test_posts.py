import pytest
pytestmark = [pytest.mark.posts]

def test_get_all_posts_returns_list(api_client):
    r = api_client.get("/posts"); assert r.status_code == 200; assert isinstance(r.json(), list)

def test_get_single_post(api_client):
    r = api_client.get("/posts/1"); assert r.status_code == 200; assert r.json()["id"] == 1

@pytest.mark.parametrize("post_id", [1, 2, 10, 50, 100])
def test_known_post_ids_return_matching_id(api_client, post_id):
    r = api_client.get(f"/posts/{post_id}"); assert r.status_code == 200; assert r.json()["id"] == post_id

def test_posts_have_expected_fields(api_client):
    post = api_client.get("/posts/1").json()
    assert {"userId", "id", "title", "body"}.issubset(post)

def test_post_field_types(api_client):
    post = api_client.get("/posts/1").json()
    assert isinstance(post["userId"], int); assert isinstance(post["id"], int)
    assert isinstance(post["title"], str); assert isinstance(post["body"], str)

def test_posts_collection_has_100_items(api_client):
    r = api_client.get("/posts"); assert r.status_code == 200; assert len(r.json()) == 100

def test_post_title_is_not_empty(api_client):
    assert api_client.get("/posts/1").json()["title"].strip()

def test_post_body_is_not_empty(api_client):
    assert api_client.get("/posts/1").json()["body"].strip()
