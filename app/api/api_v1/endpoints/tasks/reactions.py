from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_active_user
from app.core.exceptions import ObjectDoesNotExist
from app.models import Reaction, Task, User, TaskReadDetail, ReactionCreate
from app.managers import TaskManager

router = APIRouter(prefix="/reactions", tags=["task"])


@router.post("/", response_model=TaskReadDetail)
async def add_reaction(
    reaction: ReactionCreate,
    user: User = Depends(get_current_active_user),
    task_manager: TaskManager = Depends(TaskManager)
):
    return task_manager.add_reaction(reaction, user)


@router.post("/remove", response_model=Optional[TaskReadDetail])
async def remove_reaction(
    reaction: ReactionCreate,
    user: User = Depends(get_current_active_user),
):
    task = Task.get(id=reaction.task_id)
    for r in task.reactions:
        if reaction.emoji == r.emoji:
            try:
                # user_reaction = UserReaction.get(reaction_id=r.id, user_id=user.id)
                pass
            except ObjectDoesNotExist:
                return HTTPException(
                    status_code=404, detail="No reactions according to user was found."
                )

            # UserReaction.delete(user_reaction)
            if len(r.users) == 0:
                Reaction.delete(r)
            return Task.get(id=reaction.task_id)
    return HTTPException(
        status_code=404, detail="No reactions according to user was found."
    )
