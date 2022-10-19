from app.models.task import TaskCreate
from app.models.tag import TagCreate
from app.models.section import SectionCreate
from app.models.project import ProjectCreate
from app.managers.task import TaskManager
from app.managers.tag import TagManager
from app.managers.section import SectionManager
from app.managers.project import ProjectManager
from datetime import timedelta

import pytest
from fastapi import BackgroundTasks
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.db import get_session
from app.main import app
from app.managers.user import UserManager
from app.models.user import UserCreate

from .test_client import JWTAuthTestClient


@pytest.fixture
def mock_backround_tasks(mocker):
    """ The mocked background_tasks dependency """
    return mocker.MagicMock(autospec=BackgroundTasks)


@pytest.fixture(scope="session")
def client(db):
    def get_session_override():
        return db

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[BackgroundTasks] = lambda: mock_backround_tasks

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


@pytest.fixture
def project_manager(db):
    return ProjectManager(db)


@pytest.fixture
def project_schema(user):
    return ProjectCreate(name="Test project", owner_id=user.id)


@pytest.fixture
def project(project_manager, project_schema):
    project = project_manager.create(project_schema)
    yield project
    project_manager.delete(project)


@pytest.fixture
def section_manager(db):
    return SectionManager(db)


@pytest.fixture
def section_schema(project, user):
    return SectionCreate(name="Test section", project_id=project.id, owner_id=user.id)


@pytest.fixture
def section(section_manager, section_schema):
    section = section_manager.create(section_schema)
    yield section
    section_manager.delete(section)


@pytest.fixture
def task_manager(db):
    return TaskManager(db)


@pytest.fixture
def task_schema(project, user):
    return TaskCreate(name="Test task", project_id=project.id, owner_id=user.id)


@pytest.fixture
def task(task_manager, task_schema):
    task = task_manager.create(task_schema)
    yield task
    task_manager.delete(task)


@pytest.fixture
def tag_manager(db):
    return TagManager(db)


@pytest.fixture
def tag_schema(user):
    return TagCreate(name="Test tag", color="primary", owner_id=user.id)


@pytest.fixture
def tag(tag_manager, tag_schema):
    tag = tag_manager.create(tag_schema)
    yield tag
    tag_manager.delete(tag)


@pytest.fixture
def section_task(section, task_schema, task_manager):
    task_schema.project_id = None
    task_schema.section_id = section.id
    task = task_manager.create(task_schema)
    yield task
    task_manager.delete(task)

