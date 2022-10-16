from datetime import datetime, timedelta
from typing import Type

import jwt
from passlib.hash import pbkdf2_sha256
from pydantic import EmailStr

from app.api.exceptions import WrongLoginCredentials
from app.core.config import settings
from app.core.exceptions import ObjectDoesNotExist
from app.models.user import User, UserCreate, UserRead

from .base import Manager


class UserManager(Manager):
    model = User
    in_schema: UserCreate
    read_schema: UserRead

    def create(self, object: UserCreate) -> model:
        object.password = self.set_password(object.password)
        return super().create(object)

    def authenticate(self, email: EmailStr, password: str) -> User:
        try:
            user = self.one(User.email == email)
            if self.verify_password(password=password, instance=user):
                return user
            raise WrongLoginCredentials("Password doesn't match.")
        except ObjectDoesNotExist:
            raise WrongLoginCredentials("No user with such email was found.")

    def generate_access_token(
        self, subject: str, expires_delta: timedelta = None
    ) -> str:
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode = {"exp": expire, "sub": str(subject)}
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    def set_password(self, passwd: str) -> str:
        password = self._hasher().hash(passwd)
        return password

    def verify_password(self, password: str, instance: Type) -> bool:
        return self._hasher().verify(password, instance.password)

    def _hasher(self):
        return pbkdf2_sha256.using(salt=bytes(settings.SECRET_KEY.encode("utf-8")))
