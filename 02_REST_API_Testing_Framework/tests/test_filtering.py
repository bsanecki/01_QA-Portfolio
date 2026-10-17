import pytest
pytestmark = [pytest.mark.filtering]

def test_filter_posts_by_user_id(api_client):
    r = api_client.get("/posts", params={"userId": 1})
    assert r.status_code == 200; assert r.json(); assert all(x["userId"] == 1 for x in r.json())

def test_filter_comments_by_post_id(api_client):
    r = api_client.get("/comments", params={"postId": 1})
    assert r.status_code == 200; assert r.json(); assert all(x["postId"] == 1 for x in r.json())

def test_filter_todos_by_user_id(api_client):
    r = api_client.get("/todos", params={"userId": 1})
    assert r.status_code == 200; assert r.json(); assert all(x["userId"] == 1 for x in r.json())

def test_filter_albums_by_user_id(api_client):
    r = api_client.get("/albums", params={"userId": 1})
    assert r.status_code == 200; assert all(x["userId"] == 1 for x in r.json())

def test_filter_photos_by_album_id(api_client):
    r = api_client.get("/photos", params={"albumId": 1})
    assert r.status_code == 200; assert r.json(); assert all(x["albumId"] == 1 for x in r.json())

def test_start_and_limit_parameters_reduce_posts_result(api_client):
    full = api_client.get("/posts").json()
    limited = api_client.get("/posts", params={"_start": 0, "_limit": 5}).json()
    assert len(limited) == 5; assert limited == full[:5]

def test_limit_parameter_returns_requested_count(api_client):
    r = api_client.get("/comments", params={"_limit": 3})
    assert r.status_code == 200; assert len(r.json()) == 3

def test_multiple_query_parameters_can_be_combined(api_client):
    r = api_client.get("/posts", params={"userId": 1, "_limit": 2})
    assert r.status_code == 200; assert len(r.json()) == 2
    assert all(x["userId"] == 1 for x in r.json())

def test_filter_with_nonexistent_user_returns_empty_list(api_client):
    r = api_client.get("/posts", params={"userId": 999999})
    assert r.status_code == 200; assert r.json() == []
