from datetime import date, timedelta

import jwt
import pytest

from app.api.exceptions import WrongLoginCredentials
from app.core import security
from app.core.config import settings
from app.managers.user import UserManager
from app.models.user import UserCreate


def test_create_user(user_manager):
    schema = UserCreate(
        email="test@gfff.d", first_name="sss", last_name="ggg", password="12345"
    )
    user = user_manager.create(schema)

    assert user in user_manager.all()

    user_manager.delete(user)


def test_password_is_hashed(user_manager):
    schema = UserCreate(
        email="test@gfff.d", first_name="sss", last_name="ggg", password="12345"
    )
    user = user_manager.create(schema)

    assert user.password != "12345"

    user_manager.delete(user)


def test_authenticate_no_user(user_manager):
    with pytest.raises(WrongLoginCredentials):
        user_manager.authenticate("WRONG EMAIL", "WRONG PASSWORD")


def test_authenticate_wron_password(user_manager, user):
    with pytest.raises(WrongLoginCredentials):
        user_manager.authenticate(user.email, "WRONG PASSWORD")


def test_authenticate(user_manager, user):
    user_out = user_manager.authenticate(user.email, "1234")

    assert user_out.id == user.id


def test_hasher(user_manager, user, mocker):
    mocker.patch("app.managers.user.UserManager._hasher")

    user_manager.verify_password("1234", user)

    UserManager._hasher.assert_called_once()


def test_verify_password(user_manager, user):
    assert user_manager.verify_password("1234", user)


@pytest.mark.freeze_time("2022-02-02")
def test_generate_access_token_with_default_expires_delta(user_manager, user):
    token = user_manager.generate_access_token(subject=user.id)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])

    assert date.fromtimestamp(payload["exp"]) - date(2022, 2, 2) == timedelta(days=7)


@pytest.mark.freeze_time("2022-02-02")
def test_generate_access_token_with_custom_expires_delta(user_manager, user):
    token = user_manager.generate_access_token(
        subject=user.id, expires_delta=timedelta(days=10)
    )
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])

    assert date.fromtimestamp(payload["exp"]) - date(2022, 2, 2) == timedelta(days=10)
