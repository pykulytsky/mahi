from datetime import datetime, timedelta

import pytest
from sqlmodel import select

from app.models import TaskCreate
from app.models.reaction import ReactionBase
from app.models.task import Task


def test_task_update_completed_at_when_tash_is_been_completed(task_manager, project):
    task = task_manager.create(TaskCreate(name="Test task", project_id=project.id))

    assert task.completed_at is None

    updated_task = task_manager.update(task.id, is_completed=True)

    assert updated_task.completed_at is not None
    assert abs(updated_task.completed_at - datetime.now()) < timedelta(seconds=10)

    task_manager.delete(updated_task)


def test_uncomplete_task(task_manager, project):
    task = task_manager.create(
        TaskCreate(name="Test task", project_id=project.id, is_completed=True)
    )

    updated_task = task_manager.update(task.id, is_completed=False)

    assert updated_task.completed_at is None

    task_manager.delete(updated_task)


def test_permission_list(task, user):
    assert ("Allow", f"user:{user.id}", "view") in task.__acl__()
    assert ("Allow", f"user:{user.id}", "edit") in task.__acl__()
    assert ("Allow", f"user:{user.id}", "complete") in task.__acl__()
    assert ("Allow", f"user:{user.id}", "delete") in task.__acl__()
    assert ("Allow", f"user:{user.id}", "assign") in task.__acl__()


def test_project_participants_have_permissions_for_included_tasks(
    task, project, another_user, db
):
    project.participants.append(another_user)
    db.add(project)
    db.commit()
    db.refresh(project)

    assert ("Allow", f"user:{another_user.id}", "view") in task.__acl__()
    assert ("Allow", f"user:{another_user.id}", "edit") in task.__acl__()
    assert ("Allow", f"user:{another_user.id}", "complete") in task.__acl__()

    assert ("Allow", f"user:{another_user.id}", "delete") not in task.__acl__()
    assert ("Allow", f"user:{another_user.id}", "assign") not in task.__acl__()


def test_task_assignee_has_full_permissions_list(task, another_user, db):
    task.assigned_to.append(another_user)
    db.add(task)
    db.commit()
    db.refresh(task)

    assert ("Allow", f"user:{another_user.id}", "view") in task.__acl__()
    assert ("Allow", f"user:{another_user.id}", "edit") in task.__acl__()
    assert ("Allow", f"user:{another_user.id}", "complete") in task.__acl__()
    assert ("Allow", f"user:{another_user.id}", "delete") in task.__acl__()


def test_add_reaction_to_task(task_manager, task, user):
    assert task.reactions == []

    task = task_manager.add_reaction(
        reaction=ReactionBase(emoji="!"), task=task, user=user
    )

    assert len(task.reactions) == 1
    assert len(task.reactions[0].users) == 1
    assert task.reactions[0].users[0] == user


def test_remove_reaction(task_manager, task, user):
    task = task_manager.add_reaction(
        reaction=ReactionBase(emoji="!"), task=task, user=user
    )

    assert len(task.reactions) == 1

    task = task_manager.remove_reaction(
        reaction=ReactionBase(emoji="!"), task=task, user=user
    )

    assert len(task.reactions) == 0


def test_resolve_parent_container_which_is_directly_in_project(task):
    assert task.parent_container == task.project


def test_resolve_parent_container_for_subtask(subtask):
    assert subtask.parent_container == subtask.parent.project


def create_nested_task(task_manager, subtask_schema, parent_task_id: int):
    subtask_schema.parent_task_id = parent_task_id
    task = task_manager.create(subtask_schema)
    yield task
    task_manager.delete(task)


@pytest.fixture(scope="function")
def nested_task(request, task_manager, subtask_schema, task):
    target = task
    for _ in range(request.param):
        target = next(create_nested_task(task_manager, subtask_schema, target.id))
    return target


@pytest.fixture(scope="function")
def container(request, project):
    _ = request
    return project


@pytest.mark.parametrize(
    "nested_task, container",
    [
        (1, None),
        (2, None),
        (3, None),
        (4, None),
        (5, None),
        (6, None),
        (7, None),
        (8, None),
        (9, None),
        (10, None),
    ],
    indirect=["nested_task", "container"],
)
def test_resolve_parent_container_for_deeply_nested_task(nested_task, container, db):
    assert nested_task.parent_container == container

    statement = select(Task)
    results = db.exec(statement)
    for task in results:
        db.delete(task)
