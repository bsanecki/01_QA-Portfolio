import pytest
pytestmark = [pytest.mark.data_integrity]

def test_post_user_id_references_existing_user(api_client):
    post = api_client.get("/posts/1").json()
    user = api_client.get(f"/users/{post['userId']}")
    assert user.status_code == 200
    assert user.json()["id"] == post["userId"]

def test_comment_post_id_references_existing_post(api_client):
    comment = api_client.get("/comments/1").json()
    post = api_client.get(f"/posts/{comment['postId']}")
    assert post.status_code == 200

def test_todo_user_id_references_existing_user(api_client):
    todo = api_client.get("/todos/1").json()
    user = api_client.get(f"/users/{todo['userId']}")
    assert user.status_code == 200

def test_album_user_id_references_existing_user(api_client):
    album = api_client.get("/albums/1").json()
    assert api_client.get(f"/users/{album['userId']}").status_code == 200

def test_photo_album_id_references_existing_album(api_client):
    photo = api_client.get("/photos/1").json()
    assert api_client.get(f"/albums/{photo['albumId']}").status_code == 200

def test_post_filter_results_are_consistent(api_client):
    all_posts = api_client.get("/posts").json()
    filtered = api_client.get("/posts", params={"userId": 1}).json()
    assert all(post in all_posts for post in filtered)
    assert all(post["userId"] == 1 for post in filtered)
