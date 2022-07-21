from app.models import Project, Task, Tag, TagItem
import pytest


@pytest.fixture
def project(db, user):
    project = Project.manager(db).create(
        id=9999,
        name="Test proejct",
        owner=user
    )
    yield project
    db.delete(project)
    db.commit()


@pytest.fixture
def task(db, project):
    task = Task.manager(db).create(
        id=9999,
        name="Test task",
        project=project
    )
    yield task
    db.delete(task)
    db.commit()


@pytest.fixture
def tag(db, task, user):
    tag = Tag.manager(db).create(
        id=9999,
        name="Test tag",
        color="primary",
        owner=user
    )
    TagItem.manager(db).create(
        id=9999,
        tag_id=tag.id,
        task_id=task.id
    )
    yield tag
    db.delete(tag)
    db.commit()
