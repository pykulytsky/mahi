import pytest

from app.core.exceptions import ObjectDoesNotExist


def test_get_projects_list(project, client):
    res = client.get("projects")

    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["id"] == project.id


def test_get_project_by_anon_user(project, client):
    res = client.get(f"projects/{project.id}")

    assert res.status_code == 401


def test_get_project_by_owner(project, auth_client):
    res = auth_client.get(f"projects/{project.id}")

    assert res.status_code == 200
    assert res.json()["id"] == project.id
    assert res.json()["name"] == project.name
    assert res.json()["description"] == project.description
    assert res.json()["tasks"] == project.tasks
    assert res.json()["sections"] == project.sections


def test_patch_project_by_owner(project, auth_client):
    old_name = project.name
    res = auth_client.patch(f"projects/{project.id}", json={"name": "edited"})

    assert res.status_code == 200

    assert res.json()["name"] == "edited"
    assert res.json()["name"] != old_name


def test_delete_project_by_owner(project, project_manager, auth_client):
    res = auth_client.delete(f"projects/{project.id}")

    assert res.status_code == 200
    with pytest.raises(ObjectDoesNotExist):
        project_manager.get(id=project.id)


def get_user_projects(project, auth_client):
    res = auth_client.delete("projects/user")

    assert res.status_code == 200

    assert len(res.json()) == 1
    assert res.json()[0]["id"] == project.id


def test_create_project(auth_client, project_schema, user):
    res = auth_client.post("projects/", json=project_schema.dict())

    assert res.status_code == 201
    assert res.json()["name"] == project_schema.name
    assert res.json()["owner"]["id"] == user.id


def test_should_only_auth_user_create_projects(client, project_schema):
    res = client.post("projects/", json=project_schema.dict())

    assert res.status_code == 401
