import pytest
from fastapi.testclient import TestClient

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.main import app
from app.models import User

from .test_client import JWTAuthTestClient


@pytest.fixture(autouse=True, scope="session")
def create_models():
    Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


@pytest.fixture(scope="session")
def db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture()
def user(db):
    user = User.manager(db).create(
        email="test3@test.py",
        email_verified=True,
        first_name="Test",
        last_name="Testov",
        password="1234",
    )
    user.email_verified = True
    db.commit()
    db.refresh(user)
    yield user
    db.delete(user)
    db.commit()


@pytest.fixture()
def another_user(db):
    user = User.manager(db).create(
        email="test4@test.py",
        first_name="Test",
        last_name="Testov",
        password="1234",
    )
    db.commit()
    db.refresh(user)
    yield user
    db.delete(user)
    db.commit()


@pytest.fixture()
def auth_client(db, user):
    return JWTAuthTestClient(app, user=user, db=db)
