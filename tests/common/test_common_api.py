from typing import Generator
from sqlmodel import SQLModel

from app.db import create_tables, get_session


def test_global_error_handling(auth_client):
    res = auth_client.post("/tasks/9999")

    assert res.status_code == 404


def test_create_tables_on_startup(mocker):
    mocker.patch("sqlmodel.SQLModel.metadata.create_all")

    create_tables()

    SQLModel.metadata.create_all.assert_called_once()


def test_get_session():
    assert isinstance(get_session(), Generator)
