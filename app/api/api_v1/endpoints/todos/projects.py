from app import schemas
from app.api.router import AuthenticatedCrudRouter
from app.models import Project

router = AuthenticatedCrudRouter(
    model=Project,
    get_schema=schemas.Project,
    create_schema=schemas.ProjectCreate,
    update_schema=schemas.ProjectUpdate,
    prefix="/projects",
    tags=["todo"],
    owner_field_is_required=True
)
