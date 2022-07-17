from app import schemas
from app.api.router import CrudRouter
from app.models import User

from app.api.deps import get_current_active_user, get_db

from fastapi import Depends


router = CrudRouter(
    model=User,
    get_schema=schemas.User,
    create_schema=schemas.UserCreate,
    update_schema=schemas.UserUpdate,
    prefix="/users",
    tags=["users"],
)


@router.get("/me/", response_model=schemas.User)
async def get_me(
    user: User = Depends(get_current_active_user),
):
    return user
