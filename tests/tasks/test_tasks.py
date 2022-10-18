from datetime import datetime, timedelta

from app.models import TaskCreate
from app.models.reaction import ReactionBase


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


def test_project_participants_have_permissions_for_section_included_tasks(
    project, another_user, db, section_task
):
    project.participants.append(another_user)
    db.add(project)
    db.commit()
    db.refresh(project)

    assert ("Allow", f"user:{another_user.id}", "view") in section_task.__acl__()
    assert ("Allow", f"user:{another_user.id}", "edit") in section_task.__acl__()
    assert ("Allow", f"user:{another_user.id}", "complete") in section_task.__acl__()

    assert ("Allow", f"user:{another_user.id}", "delete") not in section_task.__acl__()
    assert ("Allow", f"user:{another_user.id}", "assign") not in section_task.__acl__()


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
