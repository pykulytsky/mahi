import pytest

from app.managers.project import ProjectManager
from app.models.project import ProjectCreate


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
