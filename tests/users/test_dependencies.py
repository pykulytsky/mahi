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
