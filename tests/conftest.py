from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from fastapi_sqlalchemy import db as DB

from app.db.base import Base
from app.db.session import engine
from app.main import app
from app.models import User

from .test_client import JWTAuthTestClient


@pytest.fixture(autouse=True, scope="session")
def create_models():
    Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="session")
def client():
    return TestClient(app, base_url="http://testserver/api/v1/")


@pytest.fixture(autouse=True, scope="session")
def db():
    with DB() as session:
        yield session


@pytest.fixture(scope="session")
def user(db):
    user = User.create(
        email="test3@test.py",
        email_verified=True,
        first_name="Test",
        last_name="Testov",
        password="1234",
    )
    yield user
    User.delete(user)


@pytest.fixture
def journal(user):
    return user.journal


@pytest.fixture()
def another_user(db):
    user = User.create(
        email="test4@test.py",
        first_name="Test",
        last_name="Testov",
        password="1234",
    )
    yield user
    User.delete(user)


@pytest.fixture()
def auth_client(db, user):
    return JWTAuthTestClient(app, user=user, db=db)


@pytest.fixture
def token(db, user):
    access_token_expires = timedelta(minutes=99999)
    return User.generate_access_token(
        subject=user.id, expires_delta=access_token_expires
    )


@pytest.fixture
def another_token(db, another_user):
    access_token_expires = timedelta(minutes=99999)
    return User.generate_access_token(
        subject=another_user.id, expires_delta=access_token_expires
    )
