from app import schemas
from app.api.router import AuthenticatedCrudRouter
from app.models import TodoItem

router = AuthenticatedCrudRouter(
    model=TodoItem,
    get_schema=schemas.TodoItem,
    create_schema=schemas.TodoItemCreate,
    update_schema=schemas.TodoItemUpdate,
    prefix="/todos",
    tags=["todo"],
)
