from datetime import datetime

from fastapi import BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.api.deps import get_current_active_user, get_db
from app.api.router import AuthenticatedCrudRouter
from app.models import Project, Task, User
from app.models.tasks import Section
from app.sse.tasks import remind

router = AuthenticatedCrudRouter(
    model=Task,
    get_schema=schemas.Task,
    create_schema=schemas.TaskCreate,
    update_schema=schemas.TaskUpdate,
    prefix="/tasks",
    tags=["task"],
)


@router.post("/", response_model=schemas.Task)
async def create_task(
    task_in: schemas.TaskCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    instance = Task.create(**dict(task_in))
    if task_in.remind_at is not None:
        background_tasks.add_task(remind, instance)
    return instance


@router.get("/date/{date}", response_model=list[schemas.Task])
async def get_tasks_by_date(
    date: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    raw_date = datetime.strptime(date, "%Y-%m-%d")
    owned_projects = Project.filter(owner=user)
    tasks = []
    for project in owned_projects:
        tasks += Task.filter(deadline=raw_date, project=project)
    return tasks


@router.post("/{id}/move/{project_id}", response_model=schemas.Task)
async def move_task_to_proejct(
    id: int,
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    task = Task.get(id=id)
    if task.project.owner == user:
        updated_task = Task.update(id=task.id, project_id=project_id)
        return updated_task
    else:
        raise HTTPException(status_code=400, detail="Authentication error")


@router.post("/{order}/reorder/", response_model=schemas.Task)
async def reorder_tasks(
    order: str | int,
    reorder_schema: schemas.TaskReorder,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):

    project_id, section_id = (reorder_schema.source_id, None) if reorder_schema.source_type == "project" else (None, reorder_schema.source_id)
    instance = Task.get(
        section_id=section_id,
        project_id=project_id,
        order=order
    )

    model = Section if reorder_schema.destination_type == "section" else Project
    destination = model.get(id=reorder_schema.destination_id)

    return Task.reorder(instance, destination, reorder_schema.order)
