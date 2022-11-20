from fastapi import Depends, HTTPException
from pydantic import EmailStr
from sqlmodel import Session

from app.api.deps import Permission, get_current_active_user
from app.api.router import PermissionedCrudRouter
from app.db import get_session
from app.managers import ProjectManager
from app.managers.user import UserManager
from app.models import (
    Project,
    ProjectCreate,
    ProjectRead,
    ProjectReadDetail,
    ProjectUpdate,
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


@router.get("/{id}/invite")
async def get_invitation_code(
    project: Project = Permission("invite", router._get_item()),
    manager: ProjectManager = Depends(ProjectManager),
):
    return {"code": manager.generate_invitaion_code(project.id)}


@router.get("/invitation/{code}", response_model=ProjectReadDetail)
async def accept_invitation(
    code: str,
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session),
    manager: ProjectManager = Depends(ProjectManager),
):
    project = manager.validate_invitation_code(code)
    if user not in project.participants and user != project.owner:
        project.participants.append(user)
        db.commit()
        db.refresh(project)
        return project
    else:
        raise HTTPException(
            status_code=404,
            detail="Current user is already participant of this project",
        )


@router.get("/{id}/direct-invite/{email}", response_model=ProjectReadDetail)
async def send_direct_invitation(
    email: EmailStr,
    project: Project = Permission("invite", router._get_item()),
    db: Session = Depends(get_session),
    user_manager: UserManager = Depends(UserManager),
):
    target_user = user_manager.one(User.email == email)
    if target_user not in project.participants and target_user != project.owner:
        project.participants.append(target_user)
        db.commit()
        db.refresh(project)
        return project
    else:
        raise HTTPException(
            status_code=404,
            detail="Current user is already participant of this project",
        )


@router.post("/{id}/remove-user/{email}", response_model=ProjectReadDetail)
async def remove_user_from_project(
    email: EmailStr,
    project: Project = Permission("invite", router._get_item()),
    db: Session = Depends(get_session),
    user_manager: UserManager = Depends(UserManager),
):
    target_user = user_manager.one(User.email == email)
    if target_user in project.participants and target_user != project.owner:
        project.participants.remove(target_user)
        db.commit()
        db.refresh(project)
        return project
    else:
        raise HTTPException(
            status_code=404,
            detail="User is not participant of this project",
        )
