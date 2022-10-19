import asyncio
from datetime import datetime

from jwt.api_jwt import json

from app.models import Task
from app.models.project import Project, ProjectBase
from app.models.task import TaskRead

from .kafka import produce


async def remind(task: Task) -> None:
    delay = task.remind_at.timestamp() - datetime.now().timestamp()
    if delay > 1:
        await asyncio.sleep(delay)

        await produce(
            message={
                "message_type": "remind",
                "task": TaskRead.from_orm(task).dict(),
                "timestamp": datetime.now().timestamp(),
            },
            topic=f"personal_{task.project.owner_id}",
        )


async def deadline_remind(task: Task) -> None:
    deadline = datetime.combine(task.deadline, datetime.min.time())
    deadline = deadline.replace(hours=9)
    delay = deadline.timestamp() - datetime.now().timestamp()
    if delay > 1:
        await asyncio.sleep(delay)

        await produce(
            message={
                "message_type": "deadline",
                "task": TaskRead.from_orm(task).dict(),
                "timestamp": datetime.now().timestamp(),
            },
            topic=f"personal_{task.project.owner_id}",
        )


async def project_invite(project: Project) -> None:
    await produce(
        message={
            "message_type": "invite",
            "project": ProjectBase.from_orm(project).dict(),
            "timestamp": datetime.now().timestamp(),
        }
    )
