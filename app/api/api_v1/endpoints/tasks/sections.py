from fastapi import Depends

from app.api.deps import get_current_active_user
from app.api.router import PermissionedCrudRouter
from app.managers import SectionManager
from app.models import (
    Section,
    SectionCreate,
    SectionRead,
    SectionReadDetail,
    SectionUpdate,
    User,
)

router = PermissionedCrudRouter(
    model=Section,
    manager=SectionManager,
    get_schema=SectionRead,
    create_schema=SectionCreate,
    update_schema=SectionUpdate,
    detail_schema=SectionReadDetail,
    prefix="/sections",
    tags=["task"],
    owner_field_is_required=True,
)


@router.post("/{id}/reorder", response_model=SectionReadDetail)
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
