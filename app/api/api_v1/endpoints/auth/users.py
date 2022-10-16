from fastapi import Depends

from app import schemas
from app.api.deps import get_current_active_user
from app.api.router import CrudRouter
from app.managers import UserManager
from app.models import User, UserCreate, UserRead, UserReadDetail, UserUpdate

router = CrudRouter(
    model=User,
    manager=UserManager,
    get_schema=UserRead,
    create_schema=UserCreate,
    update_schema=UserUpdate,
    detail_schema=UserReadDetail,
    prefix="/users",
    tags=["users"],
)


@router.get("/me/", response_model=schemas.User)
async def get_me(
    user: schemas.User = Depends(get_current_active_user),
):
    return user


@router.get("/me/activities", response_model=list[schemas.Activity])
async def get_my_activities(user: schemas.User = Depends(get_current_active_user)):
    return user.activities[::-1]
