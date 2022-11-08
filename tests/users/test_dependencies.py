from fastapi_permissions import Authenticated, Everyone
import pytest
from fastapi.exceptions import HTTPException

from app.api import deps
from app.models.user import User


@pytest.mark.xfail(strict=True)
def test_get_current_user(another_token):
    user = deps.get_current_user(another_token)

    assert isinstance(user, User)


def test_get_current_user_doesnt_exists(db):
    with pytest.raises(HTTPException):
        deps.get_current_user("NOT TOKEN")


def test_get_current_active_user(user):
    user_out = deps.get_current_active_user(user)

    assert isinstance(user_out, User)
    assert user_out.is_active is True


def test_get_active_user_with_unactive_user(another_user, db):
    another_user.is_active = False
    db.commit()
    db.refresh(another_user)

    with pytest.raises(HTTPException):
        deps.get_current_active_user(another_user)


def test_get_verified_user(user):
    user_out = deps.get_current_verified_user(user)

    assert isinstance(user_out, User)
    assert user_out.email_verified is True


def test_superuser_dependencies(superuser):
    assert deps.get_current_active_superuser(superuser) == superuser


def test_regular_user_with_superuser_dependencies(another_user):
    with pytest.raises(HTTPException):
        deps.get_current_active_superuser(another_user)


def test_principals_of_unauthorized_user():
    assert deps.get_active_user_principals(None) == [Everyone]


def test_principals_of_authorized_user(another_user):
    assert deps.get_active_user_principals(another_user) == [Everyone, Authenticated, f"user:{another_user.id}"]


def test_principals_of_superuser(superuser):
    assert deps.get_active_user_principals(superuser) == [Everyone, Authenticated, f"user:{superuser.id}", "role:superuser"]


def test_unverified_user(another_user):
    with pytest.raises(HTTPException):
        deps.get_current_verified_user(another_user)


def test_verified_user(user):
    assert deps.get_current_verified_user(user) == user

