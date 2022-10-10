from sqlalchemy.orm import Session
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
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user)
):
    tag_item = TagItem.manager().get(**tag_data.dict())
    TagItem.manager().delete(tag_item)
    return Task.manager().get(id=tag_data.task_id)
