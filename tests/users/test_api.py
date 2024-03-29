import jwt
from pydantic import ValidationError

from app.core.config import settings
from app.models import User


def test_get_user(client, user):
    response = client.get(f"users/{user.id}")

    assert response.status_code == 200
    assert response.json()["id"] == user.id


def test_get_me_anon_user(client):
    response = client.get("users/me/")

    assert response.status_code == 401


def test_get_all_users(client, user):
    response = client.get("users/")

    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_auth_client(auth_client):
    response = auth_client.get("users/")

    assert response.status_code == 200


def test_access_get_me(auth_client, user):
    response = auth_client.get("users/me/")

    assert response.status_code == 200
    assert response.json()["id"] == user.id


def test_api_uses_db(client, user, mocker):
    mocker.patch("app.models.User.get")
    try:
        client.get(f"users/{user.id}")
    except ValidationError:
        pass

    User.get.assert_called_once_with(id=user.id)


def test_create_user(client, db):
    users_count = len(User.all())
    response = client.post(
        "users/",
        json={
            "email": "tests@t.tt",
            "first_name": "Oleh",
            "last_name": "Pykulytsky",
            "password": "passssssword",
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == "tests@t.tt"
    assert len(User.all()) != users_count

    User.delete(User.get(id=response.json()["id"]))


def test_access_token(client, user):
    response = client.post(
        "access-token",
        headers={
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={
            "grant": "",
            "username": user.email,
            "password": "1234",
            "scope": "",
            "client_id": "",
            "client_secret": "",
        },
    )
    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"

    payload = jwt.decode(
        data["access_token"], settings.SECRET_KEY, algorithms=settings.ALGORITHM
    )

    assert "exp" in payload
    assert "sub" in payload
