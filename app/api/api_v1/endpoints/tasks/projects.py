from fastapi import Depends
from sqlalchemy.orm import Session

from app import schemas
from app.api.deps import get_current_active_user, get_db
from app.api.router import AuthenticatedCrudRouter
from app.models import Project, Task, User

router = AuthenticatedCrudRouter(
    model=Project,
    get_schema=schemas.Project,
    create_schema=schemas.ProjectCreate,
    update_schema=schemas.ProjectUpdate,
    prefix="/projects",
    tags=["task"],
    owner_field_is_required=True,
)


@router.get("/user/", response_model=list[schemas.Project])
async def get_user_projects(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return Project.manager(db).filter(owner=user)


@router.get("/{project_id}/tasks", response_model=list[schemas.Task])
async def get_tasks_by_project(
    project_id,
    skip: int = 0,
    limit: int = 100,
    order_by: str = "created",
    desc: bool = False,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    project = Project.manager(db).get(id=project_id)
    if project.show_completed_tasks:
        return Task.manager(db).filter(skip, limit, order_by, desc, project_id=project_id)

    return Task.manager(db).filter(skip, limit, order_by, desc, project_id=project_id, is_done=False)
