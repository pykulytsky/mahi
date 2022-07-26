from datetime import datetime, timedelta
from typing import Any, Type

import jwt
from passlib.hash import pbkdf2_sha256

from app.api.exceptions import WrongLoginCredentials
from app.core.config import settings
from app.core.exceptions import ObjectDoesNotExists
from app.managers.base import BaseManager, BaseManagerMixin
from app import models


class UserManager(BaseManager):
    def create(self, **fields):
        self.check_fields(**fields)
        fields["password"] = self.set_password(fields["password"])

        instance = super().create(disable_check=True, **fields)

        self.refresh(instance)

        self.create_activity_journal(user=instance)

        return instance

    def set_password(self, passwd: str) -> str:
        password = self._hasher().hash(passwd)
        return password

    @staticmethod
    def verify_password(password: str, instance: Type) -> bool:
        return UserManager._hasher().verify(password, instance.password)

    @staticmethod
    def _hasher():
        return pbkdf2_sha256.using(salt=bytes(settings.SECRET_KEY.encode("utf-8")))

    def authenticate(self, email: str, password: str):
        try:
            user = self.get(email=email)

            if self.verify_password(password, user):
                return user
            else:
                raise WrongLoginCredentials("Password didn't match.")
        except ObjectDoesNotExists:
            raise WrongLoginCredentials("No user with such email was found.")

    def generate_access_token(
        self, subject: str | Any, expires_delta: timedelta = None
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

    def create_activity_journal(self, user):
        return models.ActivityJournal.manager(self.db).create(
            user=user
        )

    def delete(self, instance):
        try:
            models.ActivityJournal.manager(self.db).delete(
                models.ActivityJournal.manager(self.db).get(user_id=instance.id)
            )
        except ObjectDoesNotExists:
            pass
        return super().delete(instance)


class UserManagerMixin(BaseManagerMixin):
    @classmethod
    def manager(cls, db):
        return UserManager(cls, db)
