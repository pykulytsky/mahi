from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app import schemas
from app.api.router import AuthenticatedCrudRouter
from app.models import TagItem, User
from app.api.deps import get_db, get_current_active_user
from app.models.tasks import Task


router = AuthenticatedCrudRouter(
    model=TagItem,
    get_schema=schemas.TagItem,
    create_schema=schemas.TagItemCreate,
    prefix="/tag_items",
    tags=["task"],
)


@router.post("/remove", response_model=schemas.Task)
async def remove_tag(
    tag_data: schemas.TagItemCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user)
):
    tag_item = await TagItem.manager(db).get(**tag_data.dict())
    TagItem.manager(db).delete(tag_item)
    return await Task.manager(db).get(id=tag_data.task_id)
