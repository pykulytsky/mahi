import json
import logging
from collections import Counter

from aiokafka import (
    AIOKafkaConsumer,
    AIOKafkaProducer,
    ConsumerRebalanceListener,
    TopicPartition,
)
from aioredis import Redis

from app.models import User

logging.basicConfig(
    format="[%(asctime)-15s] [%(levelname)s]: %(message)s",
    level=logging.ERROR,
    datefmt="%Y-%m-%d %H:%M:%S",
)

log = logging.getLogger()


class RebalancerListener(ConsumerRebalanceListener):
    def __init__(self, lock):
        self.lock = lock

    async def on_partitions_revoked(self, revoked):
        log.info("revoking, waiting on lock")
        # wait until a single batch processing is done
        async with self.lock:
            pass
        log.info("revoked")

    async def on_partitions_assigned(self, assigned):
        pass


def serializer(value):
    return json.dumps(value).encode("utf-8")


def deserializer(serialized):
    return json.loads(serialized)


async def consume(
    redis: Redis,
    user: User,
    topic: str = "default",
):
    REDIS_HASH_KEY = f"aggregated_count:{topic}:0:{user.id}"

    tp = TopicPartition(topic, 0)
    consumer = AIOKafkaConsumer(
        bootstrap_servers="localhost:9092",
        value_deserializer=deserializer,
        enable_auto_commit=False,
    )
    await consumer.start()
    consumer.assign([tp])

    # Load initial state of aggregation and last processed offset
    offset = -1
    counts = Counter()
    initial_counts = await redis.hgetall(REDIS_HASH_KEY)
    for key, state in initial_counts.items():
        state = json.loads(state)
        offset = max([offset, state["offset"]])
        counts[key] = state["count"]

    # Same as with manual commit, you need to fetch next message, so +1
    consumer.seek(tp, offset + 1)
    try:
        async for msg in consumer:
            yield {
                "event": "new_message",
                "data": {"topic": msg.topic, "value": msg.value},
            }
            try:
                key = msg.key.decode("utf-8")
                counts[key] += 1
                value = json.dumps(
                    {"count": counts[key], "offset": msg.offset})
                await redis.hset(REDIS_HASH_KEY, key, value)
            except:  # noqa
                pass
    finally:
        await consumer.stop()


async def consume_old(
    topic: str = "default",
    group_id: str | None = None,
):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers="localhost:9092",
        group_id=group_id,
        enable_auto_commit=False,
    )
    await consumer.start()

    try:
        async for message in consumer:
            yield {
                "event": "new_message",
                "id": group_id,
                "data": {
                    "topic": message.topic,
                    "key": message.key,
                    "value": message.value,
                },
            }
            await consumer.commit()
    finally:
        await consumer.stop()
        await consumer.commit()


async def produce(
    message: str | dict, topic: str = "default", key: bytes = b"default"
) -> None:
    producer = AIOKafkaProducer(
        bootstrap_servers="localhost:9092", value_serializer=serializer
    )
    # Get cluster layout and initial topic/partition leadership information
    await producer.start()
    try:
        # Produce message
        await producer.send_and_wait(topic, message, key)
    finally:
        # Wait for all pending messages to be delivered or expire.
        await producer.stop()
