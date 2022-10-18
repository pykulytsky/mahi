from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.db import get_session
from app.main import app
from app.managers.user import UserManager
from app.models.user import UserCreate

from .test_client import JWTAuthTestClient


@pytest.fixture(scope="session")
def client(db):
    def get_session_override():
        return db

    app.dependency_overrides[get_session] = get_session_override

    return TestClient(app, base_url="http://testserver/api/v1/")


@pytest.fixture(autouse=True, scope="session")
def db():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(scope="session")
def user_manager(db):
    return UserManager(db)


@pytest.fixture(scope="session")
def user_schema():
    return UserCreate(
        email="test3@test.py",
        email_verified=True,
        first_name="Test",
        last_name="Testov",
        password="1234",
    )


@pytest.fixture(scope="session")
def another_user_schema():
    return UserCreate(
        email="test4@test.py",
        first_name="Test",
        last_name="Testov",
        password="1234",
    )


@pytest.fixture(scope="session")
def user(user_manager, user_schema):
    user = user_manager.create(user_schema)
    yield user
    user_manager.delete(user)


@pytest.fixture()
def another_user(user_manager, another_user_schema):
    user = user_manager.create(another_user_schema)
    yield user
    user_manager.delete(user)


@pytest.fixture
def token(user, user_manager):
    access_token_expires = timedelta(minutes=99999)
    return user_manager.generate_access_token(
        subject=user.id, expires_delta=access_token_expires
    )


@pytest.fixture
def another_token(another_user, user_manager):
    access_token_expires = timedelta(minutes=99999)
    return user_manager.generate_access_token(
        subject=another_user.id, expires_delta=access_token_expires
    )


@pytest.fixture()
def auth_client(token):
    return JWTAuthTestClient(app, token=token)


@pytest.fixture()
def another_auth_client(another_token):
    return JWTAuthTestClient(app, token=another_token)
