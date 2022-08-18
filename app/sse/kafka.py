import logging
from datetime import datetime

from aiokafka import (
    AIOKafkaConsumer,
    AIOKafkaProducer,
    ConsumerRebalanceListener,
    TopicPartition,
)

logging.basicConfig(
    format="[%(asctime)-15s] [%(levelname)s]: %(message)s",
    level=logging.INFO,
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


async def consume(
    topic: str = "default",
    group_id: str | None = None,
    date_to_seek: datetime | None = None,
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


async def produce(message: bytes, topic: str = "default") -> None:
    producer = AIOKafkaProducer(bootstrap_servers="localhost:9092")
    await producer.start()

    try:
        await producer.send_and_wait(topic=topic, value=message)
    finally:
        await producer.stop()
