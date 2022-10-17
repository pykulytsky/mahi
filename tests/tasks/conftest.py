import pytest

from app.managers.project import ProjectManager
from app.managers.section import SectionManager
from app.managers.tag import TagManager
from app.managers.task import TaskManager
from app.models.project import ProjectCreate
from app.models.section import SectionCreate
from app.models.tag import TagCreate
from app.models.task import TaskCreate


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
def task_schema(project):
    return TaskCreate(name="Test task", project_id=project.id)


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
def tag(tag_manager, tag_schema, task, db):
    tag = tag_manager.create(tag_schema)
    task.tags.append(tag)
    db.add(task)
    db.commit()
    db.refresh(task)
    yield tag
    tag_manager.delete(tag)
