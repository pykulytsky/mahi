from app.main import app
from fastapi.testclient import TestClient
from aiokafka import AIOKafkaConsumer
from tests.conftest import fake_consume, fake_next


def test_project_room(token, monkeypatch, project):
    monkeypatch.setattr(AIOKafkaConsumer, "__aiter__", fake_consume)
    monkeypatch.setattr(AIOKafkaConsumer, "__anext__", fake_next)

    token = token.decode("utf-8")
    with TestClient(app) as client:
        response = client.get(f"/sse/project/{project.id}/{token}")

        assert response.status_code == 200
        assert response.content == b'event: test\r\ndata: {}\r\n\r\n'


def test_wrong_token(token, monkeypatch, project):
    monkeypatch.setattr(AIOKafkaConsumer, "__aiter__", fake_consume)
    monkeypatch.setattr(AIOKafkaConsumer, "__anext__", fake_next)

    token = token.decode("utf-8")
    with TestClient(app) as client:
        response = client.get(f"/sse/project/{project.id}/WRONG_TOKEN")

        assert response.status_code == 403
