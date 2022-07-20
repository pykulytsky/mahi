from app import schemas
from app.api.router import AuthenticatedCrudRouter
from app.models import TagItem

router = AuthenticatedCrudRouter(
    model=TagItem,
    get_schema=schemas.TagItem,
    create_schema=schemas.TagItemCreate,
    prefix="/tag_items",
    tags=["task"],
)
