from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.models import User
from app.api.deps import get_current_active_user, get_db
from app.models.tasks import Reaction, Task, UserReaction
from app.core.exceptions import ObjectDoesNotExist


router = APIRouter(prefix="/reactions", tags=["task"])


@router.post("/", response_model=schemas.Task)
async def add_reaction(
    reaction: schemas.ReactionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    task = Task.manager().get(id=reaction.task_id)
    for r in task.reactions:
        if reaction.emoji == r.emoji:
            UserReaction.manager().create(user_id=user.id, reaction_id=r.id)
            db.commit()
            db.refresh(task)
            return Task.manager().get(id=reaction.task_id)

    reaction = Reaction.manager().create(
        emoji=reaction.emoji,
        task_id=reaction.task_id
    )
    UserReaction.manager().create(user_id=user.id, reaction_id=reaction.id)
    db.commit()
    db.refresh(task)
    return Task.manager().get(id=reaction.task_id)


@router.post("/remove", response_model=Optional[schemas.Task])
async def remove_reaction(
    reaction: schemas.ReactionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    task = Task.manager().get(id=reaction.task_id)
    for r in task.reactions:
        if reaction.emoji == r.emoji:
            try:
                user_reaction = UserReaction.manager().get(
                    reaction_id=r.id,
                    user_id=user.id
                )
            except ObjectDoesNotExist:
                return HTTPException(status_code=404, detail="No reactions according to user was found.")

            UserReaction.manager().delete(user_reaction)
            if len(r.users) == 0:
                Reaction.manager().delete(r)
            return Task.manager().get(id=reaction.task_id)
    return HTTPException(status_code=404, detail="No reactions according to user was found.")
