from fastapi import Depends

from app.api.deps import get_current_active_user
from app.api.router import PermissionedCrudRouter
from app.managers import TagManager
from app.models import Tag, TagCreate, TagRead, TagReadDetail, TagUpdate, User

router = PermissionedCrudRouter(
    model=Tag,
    get_schema=TagRead,
    create_schema=TagCreate,
    update_schema=TagUpdate,
    detail_schema=TagReadDetail,
    manager=TagManager,
    prefix="/tags",
    tags=["task"],
    owner_field_is_required=True,
)


@router.get("/user/", response_model=list[TagRead])
async def get_user_tags(
    user: User = Depends(get_current_active_user),
    manager: TagManager = Depends(TagManager),
):
    return manager.filter(Tag.owner_id == user.id)
