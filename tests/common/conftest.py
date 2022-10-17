import pytest
from app.managers.user import UserManager

from app.models import User


@pytest.fixture
def manager(db):
    return UserManager(db)
