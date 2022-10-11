from typing import Generator

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi_permissions import Authenticated, Everyone, configure_permissions
from pydantic import ValidationError

from app import models, schemas
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/access-token",
)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(reusable_oauth2)) -> models.User | None:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = models.User.get(id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user


def get_current_verified_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not current_user.email_verified:
        raise HTTPException(status_code=400, detail="Email is not verified")
    return current_user


def get_active_user_principals(user: schemas.User = Depends(get_current_active_user)):
    if user:
        # user is logged in
        principals = [Everyone, Authenticated]
        principals.append(f"user:{user.id}")
        if user.is_superuser:
            principals.append("role:superuser")
    else:
        # user is not logged in
        principals = [Everyone]
    return principals


Permission = configure_permissions(get_active_user_principals)
