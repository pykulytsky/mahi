from fastapi import Depends

from app.api.deps import get_current_active_user
from app.api.router import CrudRouter
from app.managers import UserManager
from app.models import User, UserCreate, UserEmail, UserRead, UserReadDetail, UserUpdate

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


@router.get("/me/", response_model=UserReadDetail)
async def get_me(
    user: User = Depends(get_current_active_user),
):
    return user


@router.get("/email/{email}", response_model=list[UserEmail])
async def get_users_by_email(
    email: str,
    _: User = Depends(get_current_active_user),
    manager: UserManager = Depends(UserManager),
):
    return manager.filter(User.email.like("%" + email + "%"))
