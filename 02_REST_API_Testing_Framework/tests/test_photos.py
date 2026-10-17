import pytest
pytestmark = [pytest.mark.photos]

def test_get_photos_returns_list(api_client):
    r = api_client.get("/photos"); assert r.status_code == 200; assert isinstance(r.json(), list)

def test_photos_collection_has_5000_items(api_client):
    assert len(api_client.get("/photos").json()) == 5000

def test_single_photo_schema(api_client):
    photo = api_client.get("/photos/1").json()
    assert {"albumId", "id", "title", "url", "thumbnailUrl"}.issubset(photo)
    assert isinstance(photo["albumId"], int); assert isinstance(photo["id"], int)
    assert photo["url"].startswith("https://"); assert photo["thumbnailUrl"].startswith("https://")
