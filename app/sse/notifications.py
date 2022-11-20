import asyncio

import async_timeout
from aioredis import Redis, client, exceptions
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from fastapi_plugins import depends_redis
from sse_starlette.sse import EventSourceResponse

from app.api import deps
from app.api.deps import get_current_active_user
from app.core.config import settings
from app.managers.user import UserManager
from app.models import User

from .kafka import consume, produce
from .project import project_sse_router

sse_router = APIRouter(tags=["sse"])
sse_router.include_router(project_sse_router)


STOPWORD = "STOP"


class RetryError(Exception):
    pass


async def subscribe(pubsub: client.PubSub) -> None:
    while True:
        try:
            if not pubsub.connection:  # timing issue
                raise RetryError
            message = await pubsub.get_message(
                ignore_subscribe_messages=True, timeout=1.0
            )
            if message is not None:
                data = message["data"].decode()
                if (
                    data == STOPWORD
                ):  # a special string to indicate termination / or you may just cancel the task
                    break
                # do whatever with the received message here.
        except (RetryError, exceptions.ConnectionError):
            await asyncio.sleep(0.3)
            pubsub.connection = None  # had to manually "reset"
            try:
                await pubsub.ping()  # let it reconnect
            except exceptions.ConnectionError:
                pass
            else:
                assert pubsub.connection is not None
                await pubsub.on_connect(
                    pubsub.connection
                )  # this should have been called by aioredis, but not. :(
            continue
        except asyncio.CancelledError:
            break


@sse_router.get("/general/{token}")
async def general_chanel(
    token: str,
    redis: Redis = Depends(depends_redis),
    manager: UserManager = Depends(UserManager),
):

    user = deps.get_current_user(token, manager)
    if not user:
        raise HTTPException(403, detail="Not authenticated")

    return EventSourceResponse(consume(redis, user, "general"))


@sse_router.get("/personal/{token}")
async def personal_chanel(
    token: str,
    redis: Redis = Depends(depends_redis),
    manager: UserManager = Depends(UserManager),
):

    user = deps.get_current_user(token, manager)
    if not user:
        raise HTTPException(403, detail="Not authenticated")

    return EventSourceResponse(consume(redis, user, f"personal_{user.id}"))


@sse_router.get("/v2/general")
async def general_chanel_v2(
    request: Request,
):
    await request.app.pubsub.subscribe("general")

    async def event_generator():
        while True:
            try:
                async with async_timeout.timeout(1):
                    message = await request.app.pubsub.get_message(
                        ignore_subscribe_messages=True
                    )
                    if message is not None:
                        yield {
                            "event": "new_message",
                            "id": "general_id",
                            "retry": settings.SSE_RETRY_TIMEOUT,
                            "data": message,
                        }
                    await asyncio.sleep(settings.SSE_STREAM_DELAY)
            except asyncio.TimeoutError:
                pass

    return EventSourceResponse(event_generator())


@sse_router.get("/v2/personal/{user_token}")
async def personal_chanel_v2(
    request: Request, token: str, manager: UserManager = Depends(UserManager)
):

    user = deps.get_current_user(token, manager)
    if user:
        user = deps.get_current_active_user()
    else:
        raise HTTPException(403, detail="Not authenticated")

    await request.app.pubsub.subscribe(str(user.id))

    async def event_generator():
        while True:
            try:
                async with async_timeout.timeout(1):
                    message = await request.app.pubsub.get_message(
                        ignore_subscribe_messages=True
                    )
                    if message is not None:
                        yield {
                            "event": "new_message",
                            "id": user.id,
                            "retry": settings.SSE_RETRY_TIMEOUT,
                            "data": message,
                        }
                    await asyncio.sleep(settings.SSE_STREAM_DELAY)
            except asyncio.TimeoutError:
                pass

    return EventSourceResponse(event_generator())


async def delayed_message():
    await asyncio.sleep(1)
    await produce(
        message={"event": "members_status_update", "body": {"a": 1}}, topic="general"
    )


@sse_router.get("/test-general")
async def test_general_chanel(background_tasks: BackgroundTasks):
    background_tasks.add_task(delayed_message)
    return ""


async def delayed_personal_message(user: User):
    await asyncio.sleep(1)
    await produce(
        message={"event": "members_status_update", "body": {"a": 1}},
        topic=f"personal_{user.id}",
    )


@sse_router.get("/test-personal")
async def test_personal_chanel(
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_active_user),
):
    background_tasks.add_task(delayed_personal_message, user)


async def delayed_message_v2(redis: Redis):
    await asyncio.sleep(1)
    await redis.publish(channel="general", message=str({"message": "Hello world!"}))


@sse_router.get("/v2/test-general")
async def test_general_chanel_v2(  # noqa
    background_tasks: BackgroundTasks, redis: Redis = Depends(depends_redis)
):
    background_tasks.add_task(delayed_message_v2, redis)
    return ""


async def delayed_personal_message_v2(redis: Redis, user: User):
    await asyncio.sleep(1)
    await redis.publish(
        channel=str(user.id), message=str({"message": "Personal message"})
    )


@sse_router.get("/v2/test-personal")
async def test_personal_chanel_v2(  # noqa
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_active_user),
    redis: Redis = Depends(depends_redis),
):
    background_tasks.add_task(delayed_personal_message_v2, redis, user)
    return ""


@sse_router.get("/test")
async def test_route():
    async def numbers(minimum, maximum):
        for i in range(minimum, maximum + 1):
            await asyncio.sleep(0.9)
            yield dict(data=i)
        print("finished")

    return EventSourceResponse(numbers(1, 10))
