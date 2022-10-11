from datetime import datetime, timedelta
from typing import Any, Type

import jwt
from passlib.hash import pbkdf2_sha256

from app import models
from app.api.exceptions import WrongLoginCredentials
from app.core.config import settings
from app.core.exceptions import ObjectDoesNotExist
from app.managers.base import BaseManager


class UserManager(BaseManager):
    @classmethod
    def create(cls, **fields):
        cls.check_fields(**fields)
        fields["password"] = cls.set_password(fields["password"])

        instance = super().create(disable_check=True, **fields)

        cls.refresh(instance)

        cls.create_activity_journal(user=instance)

        return instance

    @classmethod
    def set_password(cls, passwd: str) -> str:
        password = cls._hasher().hash(passwd)
        return password

    @staticmethod
    def verify_password(password: str, instance: Type) -> bool:
        return UserManager._hasher().verify(password, instance.password)

    @staticmethod
    def _hasher():
        return pbkdf2_sha256.using(salt=bytes(settings.SECRET_KEY.encode("utf-8")))

    @classmethod
    def authenticate(cls, email: str, password: str):
        try:
            user = cls.get(email=email)

            if cls.verify_password(password, user):
                return user
            else:
                raise WrongLoginCredentials("Password didn't match.")
        except ObjectDoesNotExist:
            raise WrongLoginCredentials("No user with such email was found.")

    @classmethod
    def generate_access_token(
        cls, subject: str | Any, expires_delta: timedelta = None
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

    @classmethod
    def create_activity_journal(cls, user):
        return models.ActivityJournal.create(user=user)

    @classmethod
    def delete(cls, instance):
        try:
            models.ActivityJournal.delete(
                models.ActivityJournal.get(user_id=instance.id)
            )
        except ObjectDoesNotExist:
            pass
        return super().delete(instance)
