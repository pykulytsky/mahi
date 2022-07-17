from app import schemas
from app.api.router import AuthenticatedCrudRouter
from app.models import Project, User
from app.api.deps import get_db, get_current_active_user

from fastapi import Depends
from sqlalchemy.orm import Session


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
