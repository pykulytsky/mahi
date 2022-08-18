from datetime import datetime

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.api.deps import get_current_active_user, get_db
from app.api.router import AuthenticatedCrudRouter
from app.models import Project, Task, User

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
    user: User = Depends(get_current_active_user),
):
    raw_date = datetime.strptime(date, "%Y-%m-%d")
    owned_projects = Project.manager(db).filter(owner=user)
    tasks = []
    for project in owned_projects:
        tasks += Task.manager(db).filter(deadline=raw_date, project=project)
    return tasks


@router.post("/{id}/move/{project_id}", response_model=schemas.Task)
async def move_task_to_proejct(
    id: int,
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    task = Task.manager(db).get(id=id)
    if task.project.owner == user:
        updated_task = Task.manager(db).update(id=task.id, project_id=project_id)
        return updated_task
    else:
        raise HTTPException(status_code=400, detail="Authentication error")
