from app.api.router import CrudRouter
from app.models import User
from app import schemas


router = CrudRouter(
    model=User,
    get_schema=schemas.UserUpdate,
    create_schema=schemas.UserCreate,
    prefix="/users",
    tags=["users"]
)
