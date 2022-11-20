import json
from datetime import datetime, timedelta

import redis
from aiokafka import AIOKafkaConsumer, TopicPartition
from aioredis import Redis
from fastapi import APIRouter, Depends, HTTPException
from fastapi_permissions import has_permission
from fastapi_plugins import depends_redis
from sse_starlette.sse import EventSourceResponse

from app.api import deps
from app.managers import ProjectManager, UserManager
from app.schemas.events import Message
from app.sse.kafka import deserializer, load_initial_state, produce, produce_sync


async def set_online_status(redis: Redis, topic: str, user_id: int):
    """Add user id from set of id's of active users."""
    await redis.sadd(f"{topic}_members", user_id)
    members = map(
        lambda item: int(item),
        await redis.smembers(f"{topic}_members"),
    )
    message = Message(
        event="members_status_update", body={"members": str(list(members))}
    )
    await produce(message, topic)


def remove_online_status(topic: str, user_id: int):
    """Delete user id from set of id's of active users."""
    r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
    r.srem(f"{topic}_members", user_id)
    members = map(
        lambda item: int(item),
        r.smembers(f"{topic}_members"),
    )
    message = Message(
        event="members_status_update", body={"members": str(list(members))}
    )
    produce_sync(message, topic)


async def consume_project(
    redis: Redis,
    user_id: int,
    project_id: int,
):
    topic = f"project_{project_id}"
    REDIS_HASH_KEY = f"aggregated_count:{topic}:0:{user_id}"

    tp = TopicPartition(topic, 0)
    consumer = AIOKafkaConsumer(
        bootstrap_servers="localhost:9092",
        value_deserializer=deserializer,
        enable_auto_commit=False,
    )
    await consumer.start()
    consumer.assign([tp])

    offset, counts = await load_initial_state(redis, REDIS_HASH_KEY)
    consumer.seek(tp, offset + 1)

    await set_online_status(redis, topic, user_id)

    try:
        async for msg in consumer:
            message = Message(**msg.value)
            dt = datetime.strptime(message.dt, "%Y-%m-%d %H:%M:%S.%f")
            if dt - datetime.now() < timedelta(seconds=60):
                body = message.body
                yield {"event": message.event, "data": body}
                key = msg.key.decode("utf-8")
                counts[key] += 1
                value = json.dumps({"count": counts[key], "offset": msg.offset})
                await redis.hset(REDIS_HASH_KEY, key, value)
    finally:
        remove_online_status(f"project_{project_id}", user_id)
        await consumer.stop()


project_sse_router = APIRouter(prefix="/project", tags=["project"])


@project_sse_router.get("/{id}/{token}")
async def project_chanel(
    id: int,
    token: str,
    user_manager: UserManager = Depends(UserManager),
    manager: ProjectManager = Depends(ProjectManager),
    redis: Redis = Depends(depends_redis),
):

    user = deps.get_current_user(token, user_manager)
    if not user or not user.id:
        raise HTTPException(403, detail="Not authenticated")
    user_principals = deps.get_active_user_principals(user)

    project = manager.get(id=id)
    if has_permission(user_principals, "view", project.__acl__()):
        return EventSourceResponse(consume_project(redis, user.id, id))
    else:
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions",
            headers={"WWW-Authenticate": "Bearer"},
        )
