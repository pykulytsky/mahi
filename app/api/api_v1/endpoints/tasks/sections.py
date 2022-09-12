from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.api.router import AuthenticatedCrudRouter
from app.models import User
from app.models.tasks import Section
from app.schemas import section

router = AuthenticatedCrudRouter(
    model=Section,
    get_schema=section.Section,
    create_schema=section.SectionCreate,
    update_schema=section.SectionUpdate,
    prefix="/sections",
    tags=["task"],
)


@router.post("/{id}/reorder", response_model=section.Section)
async def reorder_section(
    id: int,
    order: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    instance = Section.manager(db).get(id=id)
    for sec in instance.project.sections:
        if sec.order >= order:
            Section.manager(db).update(sec.id, order=sec.order + 1)
    instance = Section.manager(db).update(id=instance.id, order=order)

    return instance
