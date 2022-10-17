import jwt
import pytest
from pydantic import ValidationError

from app.core.config import settings
from app.managers.user import UserManager


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


@pytest.mark.xfail(strict=True)
def test_api_uses_db(client, user, mocker):
    mocker.patch("app.managers.user.UserManager.get")
    try:
        client.get(f"users/{user.id}")
    except ValidationError:
        pass

    UserManager.get.assert_called_once_with(id=user.id)


def test_create_user(client, user_manager):
    users_count = len(user_manager.all())
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
    assert len(user_manager.all()) != users_count

    user_manager.delete(user_manager.get(id=response.json()["id"]))


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
