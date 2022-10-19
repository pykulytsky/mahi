from datetime import datetime, timedelta

import jwt
from fastapi import HTTPException
from pydantic import ValidationError

from app import schemas
from app.core.config import settings
from app.models import Project, ProjectCreate, ProjectRead

from .base import Manager


class ProjectManager(Manager):
    model = Project
    in_schema = ProjectCreate
    read_schema = ProjectRead

    def generate_invitaion_code(
        self, id: int, expires: timedelta = timedelta(hours=24)
    ) -> bytes:
        expire = datetime.utcnow() + expires
        to_encode = {"exp": expire, "sub": str(id)}
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    def validate_invitation_code(self, code: str) -> Project:
        try:
            payload = jwt.decode(
                code, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            code = schemas.TokenPayload(**payload)
            return self.get(id=int(code.sub))
        except (jwt.PyJWTError, ValidationError):
            raise HTTPException(status_code=400, detail="Wrong invitation code")
