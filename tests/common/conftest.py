import pytest

from app.managers import BaseManager
from app.models import User


@pytest.fixture
def manager(db):
    return User
