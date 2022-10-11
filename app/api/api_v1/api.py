from fastapi import APIRouter

from app.api.api_v1.endpoints.auth import authentication, users
from app.api.api_v1.endpoints.tasks import (
    projects,
    reactions,
    sections,
    tag_items,
    tags,
    task_items,
)

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(authentication.router)
api_router.include_router(projects.router)
api_router.include_router(task_items.router)
api_router.include_router(tags.router)
api_router.include_router(tag_items.router)
api_router.include_router(sections.router)
api_router.include_router(reactions.router)
