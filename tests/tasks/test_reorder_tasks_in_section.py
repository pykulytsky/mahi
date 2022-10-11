import pytest

from app.models import Section, Task


@pytest.fixture
def section(db, project):
    section = Section.create(name="test section", project_id=project.id, order=0)
    yield section
    Section.delete(section)


@pytest.fixture
def initial_task(db, section) -> Task:
    task = Task.create(name="Test task", section_id=section.id)
    yield task
    Task.delete(task)


def test_task_order_created_if_parent_is_empty(initial_task):
    assert initial_task.order == 0


def test_task_reorder_by_adding_new_task(section, db, initial_task):
    new_task = Task.create(name="Test task", section_id=section.id)

    assert new_task.section_id == section.id
    assert initial_task.section_id == section.id
    assert new_task.order == 0
    assert Task.get(id=initial_task.id).order == 1

    Task.delete(new_task)


def test_reorder_by_deleting_task(section, db):
    new_task = Task.create(name="Test task", section_id=section.id)
    another = Task.create(name="Test task", section_id=section.id)
    new = Task.get(id=new_task.id)

    assert new.order == 1
    assert another.order == 0

    Task.delete(another)
    new = Task.get(id=new_task.id)

    assert new.order == 0

    Task.delete(new)


def test_reorder_isnt_performed_by_deleting_higher_task(section, db):
    new_task = Task.create(name="Test task", section_id=section.id)
    another = Task.create(name="Test task", section_id=section.id)
    new = Task.get(id=new_task.id)

    assert another.order == 0

    Task.delete(new)
    another = Task.get(id=another.id)

    assert another.order == 0

    Task.delete(another)


def test_reorder_from_section_to_project(section, db, project):
    section_task = Task.create(name="Test task", section_id=section.id)
    project_task = Task.create(name="Test task", project_id=project.id)

    assert section_task.order == project_task.order == 0

    new_project_task = Task.reorder(section_task, project, 0)
    project_task = Task.get(id=project_task.id)

    assert new_project_task.project_id is not None
    assert new_project_task.section_id is None
    assert new_project_task.order == 0
    assert project_task.order == 1

    Task.delete(project_task)
    Task.delete(new_project_task)


def test_reorder_fromproject_to_section(section, db, project):
    section_task = Task.create(name="Test task", section_id=section.id)
    project_task = Task.create(name="Test task", project_id=project.id)

    assert section_task.order == project_task.order == 0

    new_section_task = Task.reorder(project_task, section, 0)
    section_task = Task.get(id=section_task.id)

    assert new_section_task.section_id is not None
    assert new_section_task.project_id is None
    assert new_section_task.order == 0
    assert section_task.order == 1

    Task.delete(section_task)
    Task.delete(new_section_task)
