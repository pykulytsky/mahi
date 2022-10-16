from fastapi import Depends, HTTPException
from fastapi_sqlalchemy import db

from app import schemas
from app.api.deps import Permission, get_current_active_user
from app.api.router import AuthenticatedCrudRouter
from app.models import Project, Task, User
from app.managers import ProjectManager

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
    return schemas.Project.from_orm(Project.get(id=id))


@router.get("/{id}")
async def get_project(
    project: schemas.Project = Permission("view", get_project_from_db)
):
    return project


@router.patch("/{id}", response_model=schemas.Project)
async def update_project(
    update_schema: schemas.ProjectUpdate,
    project: schemas.Project = Permission("edit", get_project_from_db),
):
    return Project.update(id=project.id, **update_schema.dict(exclude_unset=True))


@router.delete("/{id}")
async def delete_project(
    project: schemas.Project = Permission("edit", get_project_from_db)
):
    return Project.delete(Project.get(id=project.id))


@router.get("/user/", response_model=list[schemas.Project])
async def get_user_projects(
    user: User = Depends(get_current_active_user),
):
    return Project.filter(owner=user)


@router.get("/{project_id}/tasks", response_model=list[schemas.Task])
async def get_tasks_by_project(
    project_id,
    skip: int = 0,
    limit: int = 100,
    order_by: str = "created",
    desc: bool = False,
    _: User = Depends(get_current_active_user),
):
    project = Project.get(id=project_id)
    if project.show_completed_tasks:
        return Task.filter(skip, limit, order_by, desc, project_id=project_id)

    return Task.filter(
        skip, limit, order_by, desc, project_id=project_id, is_done=False
    )


@router.get("/{id}/invite")
async def get_invitation_code(
    project: schemas.Project = Permission("invite", get_project_from_db),
):
    return {"code": Project.generate_invitaion_code(project.id)}


@router.get("/invitation/{code}", response_model=schemas.Project)
async def accept_invitation(
    code: str,
    user: User = Depends(get_current_active_user)
):
    project = Project.validate_invitation_code(code)
    if user not in project.participants and user != project.owner:
        project.participants.append(user)
        db.session.commit()
        db.session.refresh(project)
        return project
    else:
        raise HTTPException(status_code=404, detail="Current user is already participant of this project")


@router.get("/{id}/direct-invite")
async def send_direct_invitation(
    project: schemas.Project = Permission("invite", get_project_from_db),
):
    pass
