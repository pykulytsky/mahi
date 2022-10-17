from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_active_user
from app.core.exceptions import ObjectDoesNotExist
from app.managers import TaskManager
from app.models import Reaction, ReactionCreate, Task, TaskReadDetail, User

router = APIRouter(prefix="/reactions", tags=["task"])


@router.post("/", response_model=TaskReadDetail)
async def add_reaction(
    reaction: ReactionCreate,
    user: User = Depends(get_current_active_user),
    task_manager: TaskManager = Depends(TaskManager),
):
    return task_manager.add_reaction(reaction, user)


@router.post("/remove", response_model=Optional[TaskReadDetail])
async def remove_reaction(
    reaction: ReactionCreate,
    user: User = Depends(get_current_active_user),
    task_manager: TaskManager = Depends(TaskManager),
):
    try:
        return task_manager.remove_reaction(reaction, user)
    except:
        raise HTTPException(status_code=404, detail="No reactions was found")
