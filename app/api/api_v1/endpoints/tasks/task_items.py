from app import schemas
from app.api.router import AuthenticatedCrudRouter
from app.models import Task, User
from app.api.deps import get_db, get_current_active_user

from fastapi import Depends
from sqlalchemy.orm import Session

from datetime import datetime


router = AuthenticatedCrudRouter(
    model=Task,
    get_schema=schemas.Task,
    create_schema=schemas.TaskCreate,
    update_schema=schemas.TaskUpdate,
    prefix="/tasks",
    tags=["task"],
)


@router.get("/date/{date}", response_model=list[schemas.Task])
async def get_tasks_by_date(
    date: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user)
):
    raw_date = datetime.strptime(date, "%Y-%m-%d")
    tasks = Task.manager(db).filter(
        owner=user,
        deadline=raw_date
    )
    return tasks
