import json

from src.api.models import User


def test_add_user(test_app, test_database):
    # Given
    client = test_app.test_client()
    # When
    resp = client.post(
        "/users",
        data=json.dumps({"username": "midCenturyDude7", "email": "mgriffes@gmail.com"}),
        content_type="application/json",
    )
    data = json.loads(resp.data.decode())
    # Then
    assert resp.status_code == 201
    assert "mgriffes@gmail.com was added!" in data["message"]


def test_add_user_invalid_json(test_app, test_database):
    # Given
    client = test_app.test_client()
    # When
    resp = client.post(
        "/users",
        data=json.dumps({}),
        content_type="application/json",
    )
    data = json.loads(resp.data.decode())
    # Then
    assert resp.status_code == 400
    assert "Input payload validation failed" in data["message"]


def test_add_user_invalid_json_keys(test_app, test_database):
    # Given
    client = test_app.test_client()
    # When
    resp = client.post(
        "/users",
        data=json.dumps({"email": "mjgriffes@comcast.net"}),
        content_type="application/json",
    )
    data = json.loads(resp.data.decode())
    # Then
    assert resp.status_code == 400
    assert "Input payload validation failed" in data["message"]


def test_add_user_duplicate_email(test_app, test_database):
    # Given
    client = test_app.test_client()
    client.post(
        "/users",
        data=json.dumps({"username": "midCenturyDude7", "email": "mgriffes@gmail.com"}),
        content_type="application/json",
    )
    # When
    resp = client.post(
        "/users",
        data=json.dumps({"username": "midCenturyDude7", "email": "mgriffes@gmail.com"}),
        content_type="application/json",
    )
    data = json.loads(resp.data.decode())
    # Then
    assert resp.status_code == 400
    assert "Sorry. That email already exists." in data["message"]


def test_single_user(test_app, test_database, add_user):
    # Given
    user = add_user("midCenturyDude7", "mgriffes@gmail.com")
    client = test_app.test_client()
    # When
    resp = client.get(f"/users/{user.id}")
    data = json.loads(resp.data.decode())
    # Then
    assert resp.status_code == 200
    assert "midCenturyDude7" in data["username"]
    assert "mgriffes@gmail.com" in data["email"]


def test_single_user_incorrect_id(test_app, test_database):
    # Given
    client = test_app.test_client()
    # When
    resp = client.get("/users/999")
    data = json.loads(resp.data.decode())
    # Then
    assert resp.status_code == 404
    assert "User 999 does not exist" in data["message"]


def test_all_users(test_app, test_database, add_user):
    # Given
    test_database.session.query(User).delete()
    add_user("midCenturyDude7", "mgriffes@gmail.com")
    add_user("Henry", "henry@gmail.com")
    client = test_app.test_client()
    # When
    resp = client.get("/users")
    data = json.loads(resp.data.decode())
    # Then
    assert resp.status_code == 200
    assert len(data) == 2
    assert "midCenturyDude7" in data[0]["username"]
    assert "mgriffes@gmail.com" in data[0]["email"]
    assert "Henry" in data[1]["username"]
    assert "henry@gmail.com" in data[1]["email"]


def test_remove_user(test_app, test_database, add_user):
    test_database.session.query(User).delete()
    user = add_user("user-to-be-removed", "remove-me@testdriven.io")
    client = test_app.test_client()
    resp_one = client.get("/users")
    data = json.loads(resp_one.data.decode())
    assert resp_one.status_code == 200
    assert len(data) == 1

    resp_two = client.delete(f"/users/{user.id}")
    data = json.loads(resp_two.data.decode())
    assert resp_two.status_code == 200
    assert 'remove-me@testdriven.io was removed!' in data['message']

    resp_three = client.get("/users")
    data = json.loads(resp_three.data.decode())
    assert resp_three.status_code == 200
    assert len(data) == 0


def test_remove_user_incorrect_id(test_app, test_database):
    client = test_app.test_client()
    resp = client.delete("/users/999")
    data = json.loads(resp.data.decode())
    assert resp.status_code == 404
    assert "User 999 does not exist" in data["message"]