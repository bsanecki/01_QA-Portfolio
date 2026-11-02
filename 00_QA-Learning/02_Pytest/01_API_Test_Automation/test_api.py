import os
import pytest
import requests


@pytest.fixture
def url():
    return os.environ["API_URL"]


def get_request(url):
    response = requests.get(url)

    return {
        "status_code": response.status_code,
        "headers": response.headers,
        "text": response.text,
        "response": response
    }


def post_request(url, data):
    response = requests.post(url, json=data)

    return {
        "status_code": response.status_code,
        "headers": response.headers,
        "text": response.text,
        "response": response
    }


def put_request(url, data):
    response = requests.put(url, json=data)

    return {
        "status_code": response.status_code,
        "headers": response.headers,
        "text": response.text,
        "response": response
    }


def patch_request(url, data):
    response = requests.patch(url, json=data)

    return {
        "status_code": response.status_code,
        "headers": response.headers,
        "text": response.text,
        "response": response
    }


def delete_request(url):
    response = requests.delete(url)

    return {
        "status_code": response.status_code,
        "headers": response.headers,
        "text": response.text,
        "response": response
    }


# GET TESTS

# Check if API returns status code 200
def test_request_status(url):
    result = get_request(url)
    assert result["status_code"] == 200


# Check if response contains data
def test_response_data(url):
    result = get_request(url)
    assert result["text"] != ""


# Check if response contains Content-Type header
def test_response_headers(url):
    result = get_request(url)
    assert "Content-Type" in result["headers"]


# Check if response has a valid Content-Type
def test_response_content_type(url):
    result = get_request(url)

    content_type = result["headers"].get("Content-Type", "")

    assert content_type != ""


# Check if JSON response contains data
def test_response_json_structure(url):
    result = get_request(url)

    if "application/json" not in result["headers"].get("Content-Type", ""):
        pytest.skip("Response is not JSON")

    data = result["response"].json()

    assert data


# Check if JSON response is a dictionary
def test_response_json_type(url):
    result = get_request(url)

    if "application/json" not in result["headers"].get("Content-Type", ""):
        pytest.skip("Response is not JSON")

    data = result["response"].json()

    assert isinstance(data, dict)


# Check if response time is acceptable
def test_response_time(url):
    result = get_request(url)

    assert result["response"].elapsed.total_seconds() < 2


# Check if response has no server error
def test_no_server_error(url):
    result = get_request(url)

    assert result["status_code"] < 500


# Check if response has valid HTTP status code
def test_valid_status_code(url):
    result = get_request(url)

    assert 200 <= result["status_code"] < 300


# Check if response contains Server header
def test_server_header(url):
    result = get_request(url)

    assert "Server" in result["headers"]


# POST TESTS

# Check if POST request creates a resource
def test_post_request():
    url = "https://jsonplaceholder.typicode.com/posts"

    data = {
        "title": "QA Test",
        "body": "Test body",
        "userId": 1
    }

    result = post_request(url, data)

    assert result["status_code"] == 201


# Check if POST response contains sent data
def test_post_response_data():
    url = "https://jsonplaceholder.typicode.com/posts"

    data = {
        "title": "QA Test",
        "body": "Test body",
        "userId": 1
    }

    result = post_request(url, data)
    response_data = result["response"].json()

    assert response_data["title"] == data["title"]
    assert response_data["body"] == data["body"]
    assert response_data["userId"] == data["userId"]


# PUT TEST

# Check if PUT request updates a resource
def test_put_request():
    url = "https://jsonplaceholder.typicode.com/posts/1"

    data = {
        "id": 1,
        "title": "Updated title",
        "body": "Updated body",
        "userId": 1
    }

    result = put_request(url, data)

    assert result["status_code"] == 200


# PATCH TEST

# Check if PATCH request updates selected data
def test_patch_request():
    url = "https://jsonplaceholder.typicode.com/posts/1"

    data = {
        "title": "Patched title"
    }

    result = patch_request(url, data)

    assert result["status_code"] == 200


# DELETE TEST

# Check if DELETE request works
def test_delete_request():
    url = "https://jsonplaceholder.typicode.com/posts/1"

    result = delete_request(url)

    assert result["status_code"] == 200


# NEGATIVE TESTS

# Check if API returns 404 for non-existing resource
def test_not_found():
    url = "https://jsonplaceholder.typicode.com/posts/999999"

    result = get_request(url)

    assert result["status_code"] == 404


# PARAMETRIZED TEST

@pytest.mark.parametrize("post_id", [1, 2, 3, 4, 5])
def test_multiple_posts(post_id):
    url = f"https://jsonplaceholder.typicode.com/posts/{post_id}"

    result = get_request(url)

    assert result["status_code"] == 200

    data = result["response"].json()

    assert data["id"] == post_id