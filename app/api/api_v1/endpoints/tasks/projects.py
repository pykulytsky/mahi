from fastapi import Depends
from sqlalchemy.orm import Session

from app import schemas
from app.api.deps import Permission, get_current_active_user, get_db
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


def get_project_from_db(id):
    return schemas.Project.from_orm(Project.manager().get(id=id))


@router.get("/{id}")
async def get_project(project: schemas.Project = Permission("view", get_project_from_db)):
    return project


@router.patch("/{id}", response_model=schemas.Project)
async def update_project(
    update_schema: schemas.ProjectUpdate,
    project: schemas.Project = Permission("edit", get_project_from_db)
):
    return Project.manager().update(
        id=project.id,
        **update_schema.dict(exclude_unset=True)
    )


@router.delete("/{id}")
async def delete_project(
    project: schemas.Project = Permission("edit", get_project_from_db)
):
    return Project.manager().delete(Project.manager().get(id=project.id))


@router.get("/user/", response_model=list[schemas.Project])
async def get_user_projects(
    user: User = Depends(get_current_active_user),
):
    return Project.manager().filter(owner=user)


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
    project = Project.manager().get(id=project_id)
    if project.show_completed_tasks:
        return Task.manager().filter(
            skip, limit, order_by, desc, project_id=project_id
        )

    return Task.manager().filter(
        skip, limit, order_by, desc, project_id=project_id, is_done=False
    )
