import pytest


@pytest.mark.skip
def test_reminder(auth_client, task_schema, mock_backround_tasks):
    task_schema.remind_at = "2022-10-10T15:15:15"
    res = auth_client.post("tasks/", json=task_schema.dict())

    assert res.status_code == 201
    assert mock_backround_tasks.add_task.assert_called_once()
