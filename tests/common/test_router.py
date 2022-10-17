import typing

import pytest
from fastapi import APIRouter

from app.api.router import CrudRouter
from app.models import Task, TaskCreate, TaskRead, TaskReadDetail
from app.managers import TaskManager


class SomeClass:
    pass


@pytest.fixture
def router() -> CrudRouter:
    return CrudRouter(
        model=Task,
        manager=TaskManager,
        get_schema=TaskRead,
        create_schema=TaskCreate,
        detail_schema=TaskReadDetail,
        prefix="/test",
    )


def test_supported_class():
    router = CrudRouter(
        model=Task,
        manager=TaskManager,
        get_schema=TaskRead,
        create_schema=TaskCreate,
        detail_schema=TaskReadDetail,
        prefix="/test",
    )

    assert len(router.routes) == 5


def test_routes_were_created(mocker):
    mocker.patch("fastapi.APIRouter.add_api_route")
    CrudRouter(
        model=Task,
        manager=TaskManager,
        get_schema=TaskRead,
        create_schema=TaskCreate,
        detail_schema=TaskReadDetail,
        prefix="/test",
    )
    assert APIRouter.add_api_route.call_count == 5


def test_routes_were_created_without_adding_create_route(mocker):
    mocker.patch("fastapi.APIRouter.add_api_route")
    CrudRouter(
        model=Task,
        manager=TaskManager,
        get_schema=TaskRead,
        create_schema=TaskCreate,
        detail_schema=TaskReadDetail,
        prefix="/test",
        add_create_route=False
    )
    assert APIRouter.add_api_route.call_count == 4


def test_retrieve_route(router):
    route = router.routes[0]

    assert route.status_code == 200
    assert route.summary == "Get all tasks"
    assert route.response_model == typing.List[TaskRead]
    assert route.path == "/test/"
    assert route.methods == {"GET"}


def test_create_route(router):
    route = router.routes[1]

    assert route.status_code == 201
    assert route.summary == "Create new task"
    assert route.response_model == TaskReadDetail
    assert route.path == "/test/"
    assert route.methods == {"POST"}


def test_get_route(router):
    route = router.routes[2]

    assert route.status_code == 200
    assert route.summary == "Get task"
    assert route.response_model == TaskReadDetail
    assert route.path == "/test/{id}"
    assert route.methods == {"GET"}


def test_update_route(router):
    route = router.routes[3]

    assert route.status_code == 200
    assert route.summary == "Patch task"
    assert route.response_model == TaskReadDetail
    assert route.path == "/test/{id}"
    assert route.methods == {"PATCH"}


def test_delete_route(router):
    route = router.routes[4]

    assert route.status_code == 200
    assert route.summary == "Delete task"
    assert route.path == "/test/{id}"
    assert route.methods == {"DELETE"}
