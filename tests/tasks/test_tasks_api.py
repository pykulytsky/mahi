from app.models.task import TaskReadDetail


def test_tasks_api_works(client, task):
    res = client.get("tasks")
    data = res.json()
    assert res.status_code == 200
    assert len(data) == 1
    assert data[0]["id"] == task.id
    assert "name" in data[0]


def test_task_detail_api_by_owner(auth_client, task):
    res = auth_client.get(f"tasks/{task.id}")
    data = res.json()

    assert res.status_code == 200
    assert data["id"] == task.id
    assert data["name"] == task.name
    assert data["description"] == task.description
    assert data["owner"]["id"] == task.owner.id
    assert data["tags"] == task.tags
    assert data["reactions"] == task.reactions
    assert "section" in data


def test_task_detail_api_another_user(another_auth_client, task):
    res = another_auth_client.get(f"tasks/{task.id}")

    assert res.status_code == 403


def test_apply_tag_by_owner(auth_client, task, tag):
    res = auth_client.post(f"tasks/{task.id}/tags/{tag.id}")
    data = res.json()

    assert res.status_code == 201
    assert TaskReadDetail.validate(data)
    assert len(data["tags"]) == 1


def test_apply_same_tag_twice(auth_client, task, tag):
    auth_client.post(f"tasks/{task.id}/tags/{tag.id}")
    res = auth_client.post(f"tasks/{task.id}/tags/{tag.id}")

    assert res.status_code == 400


def test_remove_tag(auth_client, task, tag):
    auth_client.post(f"tasks/{task.id}/tags/{tag.id}")
    res = auth_client.post(f"tasks/{task.id}/tags/{tag.id}/remove")
    data = res.json()

    assert res.status_code == 201
    assert len(data["tags"]) == 0


def test_remove_nonexistent_tag(auth_client, task, tag):
    res = auth_client.post(f"tasks/{task.id}/tags/{tag.id}/remove")

    assert res.status_code == 400
