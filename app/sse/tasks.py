import asyncio
from datetime import datetime

from fastapi import Request

from app import schemas
from app.models import Task


async def remind(request: Request, task: Task):
    delay = task.remind_at.timestamp() - datetime.now().timestamp()
    if delay > 1:
        await asyncio.sleep(delay)

        await request.app.pubsub.subscribe(str(task.project.owner.id))
        await request.app.redis.publish(
            channel=str(task.project.owner.id),
            message=str(dict(schemas.Task.from_orm(task))),
        )
