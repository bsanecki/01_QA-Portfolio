import pytest
pytestmark = [pytest.mark.albums]

def test_get_albums_returns_list(api_client):
    r = api_client.get("/albums"); assert r.status_code == 200; assert isinstance(r.json(), list)

def test_albums_collection_has_100_items(api_client):
    assert len(api_client.get("/albums").json()) == 100

def test_single_album_schema(api_client):
    album = api_client.get("/albums/1").json()
    assert {"userId", "id", "title"}.issubset(album)
    assert isinstance(album["userId"], int); assert isinstance(album["id"], int); assert isinstance(album["title"], str)
