import pytest

from app.models import Task, TaskCreate


@pytest.fixture
def initial_task(task_manager, section) -> Task:
    task = task_manager.create(TaskCreate(name="Test task", section_id=section.id))
    yield task
    task_manager.delete(task)


def test_task_order_created_if_parent_is_empty(initial_task):
    assert initial_task.order == 0


def test_task_reorder_by_adding_new_task(section, task_manager, initial_task):
    new_task = task_manager.create(TaskCreate(name="Test task", section_id=section.id))

    assert new_task.section_id == section.id
    assert initial_task.section_id == section.id
    assert new_task.order == 0
    assert task_manager.get(id=initial_task.id).order == 1

    task_manager.delete(new_task)


def test_reorder_by_deleting_task(section, task_manager):
    new_task = task_manager.create(TaskCreate(name="Test task", section_id=section.id))
    another = task_manager.create(TaskCreate(name="Test task", section_id=section.id))
    new = task_manager.get(id=new_task.id)

    assert new.order == 1
    assert another.order == 0

    task_manager.delete(another)
    new = task_manager.get(id=new_task.id)

    assert new.order == 0

    task_manager.delete(new)


def test_reorder_isnt_performed_by_deleting_higher_task(section, task_manager):
    new_task = task_manager.create(TaskCreate(name="Test task", section_id=section.id))
    another = task_manager.create(TaskCreate(name="Test task", section_id=section.id))
    new = task_manager.get(id=new_task.id)

    assert another.order == 0

    task_manager.delete(new)
    another = task_manager.get(id=another.id)

    assert another.order == 0

    task_manager.delete(another)


def test_reorder_from_section_to_project(section, task_manager, project):
    section_task = task_manager.create(TaskCreate(name="Test task", section_id=section.id))
    project_task = task_manager.create(TaskCreate(name="Test task", project_id=project.id))

    assert section_task.order == project_task.order == 0

    new_project_task = task_manager.reorder(section_task, project, 0)
    project_task = task_manager.get(id=project_task.id)

    assert new_project_task.project_id is not None
    assert new_project_task.section_id is None
    assert new_project_task.order == 0
    assert project_task.order == 1

    task_manager.delete(project_task)
    task_manager.delete(new_project_task)


def test_reorder_from_project_to_section(section, task_manager, project):
    section_task = task_manager.create(TaskCreate(name="Test task", section_id=section.id))
    project_task = task_manager.create(TaskCreate(name="Test task", project_id=project.id))

    assert section_task.order == project_task.order == 0

    new_section_task = task_manager.reorder(project_task, section, 0)
    section_task = task_manager.get(id=section_task.id)

    assert new_section_task.section_id is not None
    assert new_section_task.project_id is None
    assert new_section_task.order == 0
    assert section_task.order == 1

    task_manager.delete(section_task)
    task_manager.delete(new_section_task)
