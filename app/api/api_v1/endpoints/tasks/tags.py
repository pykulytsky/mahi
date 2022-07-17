from app import schemas
from app.api.router import AuthenticatedCrudRouter
from app.models import Tag

router = AuthenticatedCrudRouter(
    model=Tag,
    get_schema=schemas.Tag,
    create_schema=schemas.TagCreate,
    update_schema=schemas.TagUpdate,
    prefix="/tags",
    tags=["task"],
)
