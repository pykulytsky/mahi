import typing

import pytest
from fastapi import APIRouter
from pydantic import BaseModel

from app import schemas
from app.api.router import CrudRouter
from app.models import Task
from app.main import app


class SomeClass:
    pass


@pytest.fixture
def router() -> CrudRouter:
    return CrudRouter(
        model=Task,
        get_schema=schemas.Task,
        create_schema=schemas.TaskCreate,
        prefix="/test",
    )


def test_unsuported_class():
    with pytest.raises(AttributeError):
        CrudRouter(
            model=SomeClass,
            get_schema=BaseModel,
            create_schema=BaseModel,
            prefix="/test",
        )


def test_supported_class():
    router = CrudRouter(
        model=Task, get_schema=BaseModel, create_schema=BaseModel, prefix="/test"
    )

    assert len(router.routes) == 5


def test_routes_were_created(mocker):
    mocker.patch("fastapi.APIRouter.add_api_route")
    CrudRouter(
        model=Task,
        get_schema=schemas.Task,
        create_schema=schemas.TaskCreate,
        prefix="/test",
    )
    assert APIRouter.add_api_route.call_count == 5


def test_routes_were_created_without_adding_create_route(mocker):
    mocker.patch("fastapi.APIRouter.add_api_route")
    CrudRouter(
        model=Task,
        get_schema=schemas.Task,
        create_schema=schemas.TaskCreate,
        prefix="/test",
        add_create_route=False,
    )
    assert APIRouter.add_api_route.call_count == 4


def test_retrieve_route(router):
    route = router.routes[0]

    assert route.status_code == 200
    assert route.name == "_get_all"
    assert route.summary == "Get all tasks"
    assert route.response_model == typing.List[schemas.Task]
    assert route.path == "/test/"
    assert route.methods == {"GET"}


def test_create_route(router):
    route = router.routes[1]

    assert route.status_code == 201
    assert route.summary == "Create new task"
    assert route.response_model == schemas.Task
    assert route.path == "/test/"
    assert route.methods == {"POST"}


def test_get_route(router):
    route = router.routes[2]

    assert route.status_code == 200
    assert route.summary == "Get task"
    assert route.response_model == schemas.Task
    assert route.path == "/test/{id}"
    assert route.methods == {"GET"}


def test_update_route(router):
    route = router.routes[3]

    assert route.status_code == 200
    assert route.summary == "Patch task"
    assert route.response_model == schemas.Task
    assert route.path == "/test/{id}"
    assert route.methods == {"PATCH"}


def test_get_routes():
    assert False, [{"path": route.path, "name": route.name} for route in app.routes][5:]


def test_delete_route(router):
    route = router.routes[4]

    assert route.status_code == 200
    assert route.summary == "Delete task"
    assert route.path == "/test/{id}"
    assert route.methods == {"DELETE"}
