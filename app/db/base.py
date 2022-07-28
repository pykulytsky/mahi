# Import all the models, so that Base has them before being
# imported by Alembic
from app.models.tasks import Project, Tag, TagItem, Task
from app.models.user import Activity, ActivityJournal, User  # noqa

from .base_class import Base  # noqa
