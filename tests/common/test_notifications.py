import asyncio
import logging

import pytest

from app.sse.kafka import RebalancerListener, deserializer, serializer

LOGGER = logging.getLogger(__name__)


@pytest.mark.skip
def test_reminder(auth_client, task_schema, mock_backround_tasks):
    task_schema.remind_at = "2022-10-10T15:15:15"
    res = auth_client.post("tasks/", json=task_schema.dict())

    assert res.status_code == 201
    assert mock_backround_tasks.add_task.assert_called_once()


@pytest.mark.asyncio
async def test_rebalancer_logging(caplog):
    rebalancer = RebalancerListener(asyncio.Lock())
    with caplog.at_level(logging.INFO):
        await rebalancer.on_partitions_revoked(None)

    assert "revoking, waiting on lock" in caplog.text


def test_kafka_produce_result_serializer():
    message = {"topic": "test", "key": "1", "value": "100"}

    data = serializer(message)
    assert isinstance(data, bytes)


def test_kafka_consume_deserializer():
    message = {"topic": "test", "key": "1", "value": "100"}

    data = serializer(message)
    consumed_message = deserializer(data)

    assert consumed_message == message
