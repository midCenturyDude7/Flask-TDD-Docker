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
