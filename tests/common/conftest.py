import pytest

from app.models import User


@pytest.fixture
def manager(db):
    return User
