from datetime import datetime, timedelta

from app.models import Task


def test_task_update_done_at_when_tash_is_been_completed(db, project):
    task = Task.manager(db).create(name="Test task", project=project)

    assert task.done_at is None

    updated_task = Task.manager(db).update(task.id, is_done=True)

    assert updated_task.done_at is not None
    assert abs(updated_task.done_at - datetime.now()) < timedelta(seconds=10)

    Task.manager(db).delete(updated_task)


def test_uncomplete_task(db, project):
    task = Task.manager(db).create(name="Test task", project=project, is_done=True)

    assert task.done_at is not None

    updated_task = Task.manager(db).update(task.id, is_done=False)

    assert updated_task.done_at is None

    Task.manager(db).delete(updated_task)
