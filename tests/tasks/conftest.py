import pytest

from app.models import Project, Tag, TagItem, Task


@pytest.fixture
def project(db, user):
    project = Project.create(name="Test proejct", owner=user)
    yield project
    Project.delete(project)


@pytest.fixture
def task(db, project):
    task = Task.create(name="Test task", project_id=project.id)
    yield task
    Task.delete(task)


@pytest.fixture
def tag(db, task, user):
    tag = Tag.create(ame="Test tag", color="primary", owner=user)
    tag_item = TagItem.create(tag_id=tag.id, task_id=task.id)
    yield tag
    Tag.delete(tag)
    TagItem.delete(tag_item)
