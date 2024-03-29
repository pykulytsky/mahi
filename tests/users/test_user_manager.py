import pytest

from app.api.exceptions import WrongLoginCredentials
from app.models.user import ActivityJournal, User


def test_create_user(db):
    user = User.create(
        email="test@gfff.d", first_name="sss", last_name="ggg", password="12345"
    )

    assert user in User.all()

    User.delete(user)


def test_password_is_hashed(db):
    user = User.create(
        email="test@gfffa.d", first_name="sss", last_name="ggg", password="12345"
    )

    assert user.password != "12345"

    User.delete(user)


def test_authenticate_no_user(db):
    with pytest.raises(WrongLoginCredentials):
        User.authenticate("WRONG EMAIL", "WRONG PASSWORD")


def test_authenticate_wron_password(db, user):
    with pytest.raises(WrongLoginCredentials):
        User.authenticate(user.email, "WRONG PASSWORD")


def test_authenticate(db, user):
    user_out = User.authenticate(user.email, "1234")

    assert user_out.id == user.id


def test_hasher(db, user, mocker):
    mocker.patch("app.managers.users.UserManager._hasher")

    User.verify_password("1234", user)

    User._hasher.assert_called_once()


def test_verify_password(db, user):
    assert User.verify_password("1234", user)


def test_activity_journal_is_created(db, mocker):
    mocker.patch("app.managers.base.BaseManager.create")

    try:
        User.create(
            email="test@tttt.t",
            password="1234",
            first_name="Oleh",
            last_name="Pykulytsky",
        )
    except AttributeError:
        pass

    ActivityJournal.create.assert_called_once()


def test_activity_journal(db):
    user = User.create(
        email="test@tttt.t", password="1234", first_name="Oleh", last_name="Pykulytsky"
    )

    assert ActivityJournal.exists(user_id=user.id)

    User.delete(user)
