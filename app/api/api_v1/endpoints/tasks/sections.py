from fastapi import Depends

from app.api.deps import get_current_active_user
from app.api.router import AuthenticatedCrudRouter
from app.models import Section, User
from app.schemas import section

router = AuthenticatedCrudRouter(
    model=Section,
    get_schema=section.Section,
    create_schema=section.SectionCreate,
    update_schema=section.SectionUpdate,
    prefix="/sections",
    tags=["task"],
    owner_field_is_required=True,
)


@router.post("/{id}/reorder", response_model=section.Section)
async def reorder_section(
    id: int,
    order: int,
    _: User = Depends(get_current_active_user),
):
    instance = Section.get(id=id)
    for sec in instance.project.sections:
        if sec.order >= order:
            Section.update(sec.id, order=sec.order + 1)
    instance = Section.update(id=instance.id, order=order)

    return instance
