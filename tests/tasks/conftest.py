import pytest

from app.models import Project, Tag, TagItem, Task


@pytest.fixture
def project(db, user):
    project = Project.manager().create(name="Test proejct", owner=user)
    yield project
    Project.manager().delete(project)


@pytest.fixture
def task(db, project):
    task = Task.manager().create(name="Test task", project_id=project.id)
    yield task
    Task.manager().delete(task)


@pytest.fixture
def tag(db, task, user):
    tag = Tag.manager().create(ame="Test tag", color="primary", owner=user)
    tag_item = TagItem.manager().create(tag_id=tag.id, task_id=task.id)
    yield tag
    Tag.manager().delete(tag)
    TagItem.manager().delete(tag_item)
