from app import schemas
from app.api.router import CrudRouter
from app.models import User

router = CrudRouter(
    model=User,
    get_schema=schemas.User,
    create_schema=schemas.UserCreate,
    update_schema=schemas.UserUpdate,
    prefix="/users",
    tags=["users"],
)
