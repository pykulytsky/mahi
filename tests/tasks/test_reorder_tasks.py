import pytest

from app.models import Task


@pytest.fixture
def initial_task(db, project) -> Task:
    task = Task.manager(db).create(name="Test task", project_id=project.id)
    yield task
    Task.manager(db).delete(task)


def test_task_order_created_if_parent_is_empty(initial_task):
    assert initial_task.order == 0


def test_task_reorder_by_adding_new_task(project, db, initial_task):
    new_task = Task.manager(db).create(name="Test task", project_id=project.id)

    assert new_task.order == 0
    assert Task.manager(db).get(id=initial_task.id).order == 1

    Task.manager(db).delete(new_task)


def test_reorder_by_deleting_task(project, db):
    new_task = Task.manager(db).create(name="Test task", project_id=project.id)
    another = Task.manager(db).create(name="Test task", project_id=project.id)
    new = Task.manager(db).get(id=new_task.id)

    assert new.order == 1
    assert another.order == 0

    Task.manager(db).delete(another)
    new = Task.manager(db).get(id=new_task.id)

    assert new.order == 0

    Task.manager(db).delete(new)


def test_reorder_isnt_performed_by_deleting_higher_task(project, db):
    new_task = Task.manager(db).create(name="Test task", project_id=project.id)
    another = Task.manager(db).create(name="Test task", project_id=project.id)
    new = Task.manager(db).get(id=new_task.id)

    assert another.order == 0

    Task.manager(db).delete(new)
    another = Task.manager(db).get(id=another.id)

    assert another.order == 0

    Task.manager(db).delete(another)


def test_create_task_with_custom_order(db, project):
    new_task = Task.manager(db).create(name="Test task", project_id=project.id)
    another = Task.manager(db).create(
        name="Test task", project_id=project.id, order=new_task.order + 1
    )
    new = Task.manager(db).get(id=new_task.id)

    assert new.order == 0
    assert another.order == 1

    Task.manager(db).delete(another)
    Task.manager(db).delete(new)


def test_reorder_from_project_to_project(db, project):
    new_task = Task.manager(db).create(name="Test task", project_id=project.id)
    another = Task.manager(db).create(name="Test task", project_id=project.id)

    assert another.order == 0

    another_updated = Task.manager(db).reorder(another, project, 1)
    new_updated = Task.manager(db).get(id=new_task.id)

    assert another_updated.order == 1
    assert new_updated.order == 0

    Task.manager(db).delete(another_updated)
    Task.manager(db).delete(new_updated)
