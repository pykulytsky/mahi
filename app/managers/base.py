from typing import Type

from fastapi import Depends
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.sql.elements import BinaryExpression
from sqlmodel import Session, SQLModel, select

from app.core.exceptions import ObjectDoesNotExist
from app.db import get_session


class Manager:
    model: Type[SQLModel] | None = SQLModel
    in_schema: Type[SQLModel] | None = SQLModel

    def __init__(self, session: Session = Depends(get_session)) -> None:
        if not any([self.model, self.in_schema]):
            raise AttributeError(
                "Set attributes model, in_schema, read_schema for exact class."
            )
        self.session = session

    def get(self, id: int) -> model:
        object = self.session.get(self.model, id)
        if object:
            return object
        raise ObjectDoesNotExist(self.model, id)

    def one(
        self,
        *expressions: list[BinaryExpression | bool],
    ):
        stmt = select(self.model).where(*expressions)
        res = self.session.exec(stmt)
        try:
            return res.one()
        except (MultipleResultsFound, NoResultFound):
            raise ObjectDoesNotExist(self.model)

    def create(self, object: in_schema) -> model:
        db_object = self.model.from_orm(object)
        self.session.add(db_object)
        self.session.commit()
        self.session.refresh(db_object)

        return db_object

    def update(self, id, **updated_fields):
        instance = self.get(id=id)

        for field in updated_fields:
            setattr(instance, field, updated_fields[field])

        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)

        return instance

    def all(self, limit: int = 100, offset: int = 0) -> list[model]:
        stmt = select(self.model).offset(offset).limit(limit)
        res = self.session.exec(stmt).all()
        return res

    def filter(
        self,
        *expressions: list[BinaryExpression | bool],
        limit: int = 100,
        offset: int = 0,
    ) -> list[model]:
        stmt = select(self.model).where(*expressions).offset(offset).limit(limit)
        res = self.session.exec(stmt).all()
        return res

    def exists(self, *expressions: list[BinaryExpression | bool]) -> model | None:
        stmt = select(self.model).where(*expressions)
        res = self.session.exec(stmt)
        try:
            res.one()
            return True
        except (MultipleResultsFound, NoResultFound):
            return False

    def delete(self, instance: model) -> None:
        self.session.delete(instance)
        self.session.commit()
