from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_permissions import Allow
from sqlalchemy.orm import Session

from app import schemas
from app.api import deps
from app.api.exceptions import WrongLoginCredentials
from app.core.config import settings
from app.models import User

router = APIRouter(tags=["auth"])


@router.post("/access-token", response_model=schemas.Token)
def get_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    try:
        user = User.authenticate(email=form_data.username, password=form_data.password)
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return {
            "access_token": User.generate_access_token(
                subject=user.id, expires_delta=access_token_expires
            ),
            "token_type": "bearer",
        }
    except WrongLoginCredentials as e:
        raise HTTPException(status_code=403, detail=str(e))


example_acl = [(Allow, "user:156", "view")]


@router.get("/test")
async def test_permission(acls: list = deps.Permission("view", example_acl)):
    return {"status": "OK"}
