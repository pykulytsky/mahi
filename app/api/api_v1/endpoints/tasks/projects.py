from fastapi import Depends, HTTPException
from fastapi_sqlalchemy import db

from app.api.deps import Permission, get_current_active_user
from app.api.router import PermissionedCrudRouter
from app.managers import ProjectManager
from app.models import (
    Project,
    ProjectCreate,
    ProjectRead,
    ProjectReadDetail,
    ProjectUpdate,
    Task,
    TaskRead,
    User,
)

router = PermissionedCrudRouter(
    model=Project,
    manager=ProjectManager,
    get_schema=ProjectRead,
    detail_schema=ProjectReadDetail,
    create_schema=ProjectCreate,
    update_schema=ProjectUpdate,
    prefix="/projects",
    tags=["task"],
    owner_field_is_required=True,
)


@router.get("/user/", response_model=list[ProjectRead])
async def get_user_projects(
    user: User = Depends(get_current_active_user),
    manager: ProjectManager = Depends(ProjectManager),
):
    return manager.filter(Project.owner_id == user.id)


@router.get("/user/detail", response_model=list[ProjectReadDetail])
async def get_detail_user_projects(
    user: User = Depends(get_current_active_user),
    manager: ProjectManager = Depends(ProjectManager),
):
    return manager.filter(Project.owner_id == user.id)


@router.get("/{project_id}/tasks", response_model=list[TaskRead])
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
        skip, limit, order_by, desc, project_id=project_id, is_completed=False
    )


@router.get("/{id}/invite")
async def get_invitation_code(
    project: Project = Permission("invite", router._get_item()),
):
    return {"code": Project.generate_invitaion_code(project.id)}


@router.get("/invitation/{code}", response_model=ProjectReadDetail)
async def accept_invitation(code: str, user: User = Depends(get_current_active_user)):
    project = Project.validate_invitation_code(code)
    if user not in project.participants and user != project.owner:
        project.participants.append(user)
        db.session.commit()
        db.session.refresh(project)
        return project
    else:
        raise HTTPException(
            status_code=404,
            detail="Current user is already participant of this project",
        )


@router.get("/{id}/direct-invite")
async def send_direct_invitation(
    project: Project = Permission("invite", router._get_item()),
):
    pass
