import pytest
from datetime import datetime, timedelta

from app.models import Task, TaskCreate


def test_task_update_completed_at_when_tash_is_been_completed(task_manager, project):
    task = task_manager.create(TaskCreate(name="Test task", project_id=project.id))

    assert task.completed_at is None

    updated_task = task_manager.update(task.id, is_completed=True)

    assert updated_task.completed_at is not None
    assert abs(updated_task.completed_at - datetime.now()) < timedelta(seconds=10)

    task_manager.delete(updated_task)


def test_uncomplete_task(task_manager, project):
    task = task_manager.create(TaskCreate(name="Test task", project_id=project.id, is_completed=True))

    updated_task = task_manager.update(task.id, is_completed=False)

    assert updated_task.completed_at is None

    task_manager.delete(updated_task)
