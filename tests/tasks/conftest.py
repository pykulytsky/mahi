import pytest

from app.models import Project, Tag, TagItem, Task


@pytest.fixture
def project(db, user):
    project = Project.manager(db).create(name="Test proejct", owner=user)
    yield project
    Project.manager(db).delete(project)


@pytest.fixture
def task(db, project):
    task = Task.manager(db).create(name="Test task", project_id=project.id)
    yield task
    Task.manager(db).delete(task)


@pytest.fixture
def tag(db, task, user):
    tag = Tag.manager(db).create(ame="Test tag", color="primary", owner=user)
    tag_item = TagItem.manager(db).create(tag_id=tag.id, task_id=task.id)
    yield tag
    Tag.manager(db).delete(tag)
    TagItem.manager(db).delete(tag_item)
