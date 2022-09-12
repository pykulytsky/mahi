import pytest

from app.models import Section, Task


@pytest.fixture
def section(db, project):
    section = Section.manager(db).create(
        name="test section", project_id=project.id, order=0
    )
    yield section
    Section.manager(db).delete(section)


@pytest.fixture
def initial_task(db, section) -> Task:
    task = Task.manager(db).create(name="Test task", section_id=section.id)
    yield task
    Task.manager(db).delete(task)


def test_task_order_created_if_parent_is_empty(initial_task):
    assert initial_task.order == 0


def test_task_reorder_by_adding_new_task(section, db, initial_task):
    new_task = Task.manager(db).create(name="Test task", section_id=section.id)

    assert new_task.section_id == section.id
    assert initial_task.section_id == section.id
    assert new_task.order == 0
    assert Task.manager(db).get(id=initial_task.id).order == 1

    Task.manager(db).delete(new_task)


def test_reorder_by_deleting_task(section, db):
    new_task = Task.manager(db).create(name="Test task", section_id=section.id)
    another = Task.manager(db).create(name="Test task", section_id=section.id)
    new = Task.manager(db).get(id=new_task.id)

    assert new.order == 1
    assert another.order == 0

    Task.manager(db).delete(another)
    new = Task.manager(db).get(id=new_task.id)

    assert new.order == 0

    Task.manager(db).delete(new)


def test_reorder_isnt_performed_by_deleting_higher_task(section, db):
    new_task = Task.manager(db).create(name="Test task", section_id=section.id)
    another = Task.manager(db).create(name="Test task", section_id=section.id)
    new = Task.manager(db).get(id=new_task.id)

    assert another.order == 0

    Task.manager(db).delete(new)
    another = Task.manager(db).get(id=another.id)

    assert another.order == 0

    Task.manager(db).delete(another)


def test_reorder_from_section_to_project(section, db, project):
    section_task = Task.manager(db).create(name="Test task", section_id=section.id)
    project_task = Task.manager(db).create(name="Test task", project_id=project.id)

    assert section_task.order == project_task.order == 0

    new_project_task = Task.manager(db).reorder(section_task, project, 0)
    project_task = Task.manager(db).get(id=project_task.id)

    assert new_project_task.project_id is not None
    assert new_project_task.section_id is None
    assert new_project_task.order == 0
    assert project_task.order == 1

    Task.manager(db).delete(project_task)
    Task.manager(db).delete(new_project_task)


def test_reorder_fromproject_to_section(section, db, project):
    section_task = Task.manager(db).create(name="Test task", section_id=section.id)
    project_task = Task.manager(db).create(name="Test task", project_id=project.id)

    assert section_task.order == project_task.order == 0

    new_section_task = Task.manager(db).reorder(project_task, section, 0)
    section_task = Task.manager(db).get(id=section_task.id)

    assert new_section_task.section_id is not None
    assert new_section_task.project_id is None
    assert new_section_task.order == 0
    assert section_task.order == 1

    Task.manager(db).delete(section_task)
    Task.manager(db).delete(new_section_task)
