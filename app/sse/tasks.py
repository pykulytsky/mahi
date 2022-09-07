import asyncio
from datetime import datetime

from app import schemas
from app.models import Task

from .kafka import produce


async def remind(task: Task) -> None:
    delay = task.remind_at.timestamp() - datetime.now().timestamp()
    if delay > 1:
        await asyncio.sleep(delay)

        await produce(
            message={
                "message_type": "remind",
                "task": schemas.TaskJSONSerializable.from_orm(task).dict(),
                "timestamp": datetime.now().timestamp(),
            },
            topic=f"personal_{task.project.owner.id}",
        )
