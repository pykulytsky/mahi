import pytest

from app.models import Task, TaskCreate


@pytest.fixture
def initial_task(task_manager, project) -> Task:
    task = task_manager.create(TaskCreate(name="Test task", project_id=project.id))
    yield task
    task_manager.delete(task)


def test_task_order_created_if_parent_is_empty(initial_task):
    assert initial_task.order == 0


def test_task_reorder_by_adding_new_task(project, task_manager, initial_task):
    new_task = task_manager.create(TaskCreate(name="Test task", project_id=project.id))

    assert new_task.order == 0
    assert task_manager.get(id=initial_task.id).order == 1

    task_manager.delete(new_task)


def test_reorder_by_deleting_task(project, task_manager):
    new_task = task_manager.create(TaskCreate(name="Test task", project_id=project.id))
    another = task_manager.create(TaskCreate(name="Test task", project_id=project.id))
    new = task_manager.get(id=new_task.id)

    assert new.order == 1
    assert another.order == 0

    task_manager.delete(another)
    new = task_manager.get(id=new_task.id)

    assert new.order == 0

    task_manager.delete(new)


def test_reorder_isnt_performed_by_deleting_higher_task(project, task_manager):
    new_task = task_manager.create(TaskCreate(name="Test task", project_id=project.id))
    another = task_manager.create(TaskCreate(name="Test task", project_id=project.id))
    new = task_manager.get(id=new_task.id)

    assert another.order == 0

    task_manager.delete(new)
    another = task_manager.get(id=another.id)

    assert another.order == 0

    task_manager.delete(another)


def test_create_task_with_custom_order(task_manager, project):
    new_task = task_manager.create(TaskCreate(name="Test task", project_id=project.id))
    another = task_manager.create(
        TaskCreate(name="Test task", project_id=project.id, order=new_task.order + 1)
    )
    new = task_manager.get(id=new_task.id)

    assert new.order == 0
    assert another.order == 1

    task_manager.delete(another)
    task_manager.delete(new)


def test_reorder_from_project_to_project(task_manager, project):
    new_task = task_manager.create(TaskCreate(name="Test task", project_id=project.id))
    another = task_manager.create(TaskCreate(name="Test task", project_id=project.id))

    assert another.order == 0

    another_updated = task_manager.reorder(another, project, 1)
    new_updated = task_manager.get(id=new_task.id)

    assert another_updated.order == 1
    assert new_updated.order == 0

    task_manager.delete(another_updated)
    task_manager.delete(new_updated)
