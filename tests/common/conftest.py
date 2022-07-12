import pytest

from app.models import User
from app.managers import BaseManager


@pytest.fixture
def manager(db):
    return BaseManager(User, db)
