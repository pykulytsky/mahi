import asyncio

import anyio
from fastapi_plugins.plugin import fastapi
import pytest
from aiokafka import AIOKafkaConsumer
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sse_starlette import EventSourceResponse

from app.main import app
from tests.conftest import fake_consume, fake_next


@pytest.mark.parametrize(
    "input,expected",
    [
        ("integer", b"data: 1\r\n\r\n"),
        ("dict1", b"data: 1\r\n\r\n"),
        ("dict2", b"event: message\r\ndata: 1\r\n\r\n"),
    ],
)
def test_sync_event_source_response(input, expected):
    async def app(scope, receive, send):
        async def numbers(minimum, maximum):
            for i in range(minimum, maximum + 1):
                await asyncio.sleep(0.1)
                if input == "integer":
                    yield i
                elif input == "dict1":
                    yield dict(data=i)
                elif input == "dict2":
                    yield dict(data=i, event="message")

        generator = numbers(1, 5)
        response = EventSourceResponse(generator, ping=0.2)  # type: ignore
        await response(scope, receive, send)

    client = TestClient(app)
    response = client.get("/")
    assert response.content.decode().count("ping") == 2
    assert expected in response.content


@pytest.mark.skipif(fastapi.__version__ < "0.82.0", reason="Missing eventloop in FastAPI dependencies")
def test_general_channel(token, monkeypatch):
    monkeypatch.setattr(AIOKafkaConsumer, "__aiter__", fake_consume)
    monkeypatch.setattr(AIOKafkaConsumer, "__anext__", fake_next)

    token = token.decode("utf-8")
    with TestClient(app) as client:
        response = client.get(f"/sse/general/{token}")

        assert response.status_code == 200
        assert response.content == b"event: test\r\ndata: {}\r\n\r\n"


def test_general_channel_with_wrong_credentials():
    with TestClient(app) as client:
        response = client.get("/sse/general/WRONG_TOKEN")

        assert response.status_code == 403


@pytest.mark.skipif(fastapi.__version__ < "0.82.0", reason="Missing eventloop in FastAPI dependencies")
def test_personal_chanel(token, monkeypatch):
    monkeypatch.setattr(AIOKafkaConsumer, "__aiter__", fake_consume)
    monkeypatch.setattr(AIOKafkaConsumer, "__anext__", fake_next)

    token = token.decode("utf-8")
    with TestClient(app) as client:
        response = client.get(f"/sse/personal/{token}")

        assert response.status_code == 200
        assert response.content == b"event: test\r\ndata: {}\r\n\r\n"


def test_personal_channel_with_wrong_credentials():
    with TestClient(app) as client:
        response = client.get("/sse/personal/WRONG_TOKEN")

        assert response.status_code == 403


@pytest.mark.anyio
async def test_general_channel_is_endless():
    with pytest.raises(TimeoutError):
        async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
            with anyio.fail_after(1) as _:
                async with anyio.create_task_group() as _:
                    async with client.stream("GET", "/sse/test") as _:
                        pass
