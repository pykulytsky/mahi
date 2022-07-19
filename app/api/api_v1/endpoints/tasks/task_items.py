from app import schemas
from app.api.router import AuthenticatedCrudRouter
from app.models import Task, User
from app.api.deps import get_db, get_current_active_user

from fastapi import Depends
from sqlalchemy.orm import Session


router = AuthenticatedCrudRouter(
    model=Task,
    get_schema=schemas.Task,
    create_schema=schemas.TaskCreate,
    update_schema=schemas.TaskUpdate,
    prefix="/tasks",
    tags=["task"],
)


@router.get("/project/{project_id}", response_model=list[schemas.Task])
async def get_tasks_by_project(
    project_id,
    skip: int = 0,
    limit: int = 100,
    order_by: str = "created",
    desc: bool = False,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user)
):
    return Task.manager(db).filter(skip, limit, order_by, desc, project_id=project_id)
