import pytest

from app.managers.user import UserManager


@pytest.fixture
def manager(db):
    return UserManager(db)
