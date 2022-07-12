from fastapi import APIRouter

from app.api.api_v1.endpoints.auth import authentication, users

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(authentication.router)
