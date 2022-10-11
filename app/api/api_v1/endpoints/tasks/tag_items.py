from fastapi import Depends
from sqlalchemy.orm import Session

from app import schemas
from app.api.deps import get_current_active_user, get_db
from app.api.router import AuthenticatedCrudRouter
from app.models import TagItem, User
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
    _: User = Depends(get_current_active_user),
):
    tag_item = TagItem.get(**tag_data.dict())
    TagItem.delete(tag_item)
    return Task.get(id=tag_data.task_id)
