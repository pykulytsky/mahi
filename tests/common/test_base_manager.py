import pytest

from app.core.exceptions import ImproperlyConfigured
from app.managers import BaseManager


class SomeClass:
    pass


def test_class_validation(db):
    with pytest.raises(ImproperlyConfigured):
        BaseManager(SomeClass, db)


def test_manager_all(manager, user):
    assert manager.all()[0] == user


def test_manager_get(user, manager):
    assert manager.get(id=user.id) == user


def test_use_unsuported_fields(user, manager):
    with pytest.raises(ValueError):
        manager.get(wrong_field_name="")


def test_get_with_multiply_fields(manager, user):
    assert (
        manager.get(id=user.id, email=user.email, first_name=user.first_name)
        == user
    )


def test_filter(manager, user):
    assert (
        manager.filter(
            id=user.id,
            email=user.email,
            first_name=user.first_name
        )[0] == user
    )


def test_check_fields(mocker, manager, user):
    mocker.patch("app.managers.base.BaseManager.check_fields")

    manager.get(id=user.id)

    manager.check_fields.assert_called_once_with(id=user.id)


def test_create(manager):
    user = manager.create(email="world", password="!!!", first_name="test", last_name="tetest")

    assert manager.exists(email="world", first_name="test")

    manager.delete(user)


@pytest.mark.skip()
def test_order_by(manager):
    user = manager.create(email="world", password="!!!", first_name="test", last_name="tetest")
    older_one = manager.create(
        email="world1", password="!!!", first_name="test", last_name="tetest"
    )

    assert older_one == manager.all(order_by="created", desc=False)[0]

    manager.delete(user)
    manager.delete(older_one)


def test_update(manager, user):
    first_name = user.first_name

    manager.update(user.id, first_name="changed")

    assert first_name != "changed"
    assert manager.get(id=user.id).first_name == "changed"
