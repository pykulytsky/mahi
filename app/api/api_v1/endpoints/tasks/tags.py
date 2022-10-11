from fastapi import Depends
from sqlalchemy.orm import Session

from app import schemas
from app.api.deps import get_current_active_user
from app.api.router import AuthenticatedCrudRouter
from app.models import Tag, User

router = AuthenticatedCrudRouter(
    model=Tag,
    get_schema=schemas.Tag,
    create_schema=schemas.TagCreate,
    update_schema=schemas.TagUpdate,
    prefix="/tags",
    tags=["task"],
    owner_field_is_required=True,
)


@router.get("/user/", response_model=list[schemas.Tag])
async def get_user_tags(
    user: User = Depends(get_current_active_user)
):
    return Tag.filter(owner_id=user.id)
