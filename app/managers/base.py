from typing import List, Type, Union

from fastapi_sqlalchemy import db
from sqlalchemy import MetaData

from app.core.exceptions import ObjectDoesNotExist


class BaseManager:
    @classmethod
    def create(cls, disable_check: bool = False, **fields):
        if not disable_check:
            cls.check_fields(**fields)
        instance = cls(**fields)

        db.session.add(instance)
        db.session.commit()
        db.session.refresh(instance)
        return instance

    @classmethod
    def delete(cls, instance):
        db.session.delete(instance)
        db.session.commit()

    @classmethod
    def all(
        cls,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "created",
        desc: bool = False,
    ) -> List[Type]:
        try:
            if desc:
                return (
                    db.session.query(cls)
                    .order_by(getattr(cls, order_by).desc())
                    .offset(skip)
                    .limit(limit)
                    .all()
                )
            return (
                db.session.query(cls)
                .order_by(getattr(cls, order_by))
                .offset(skip)
                .limit(limit)
                .all()
            )
        except AttributeError:
            return db.session.query(cls).offset(skip).limit(limit).all()

    @classmethod
    def get(cls, **fields) -> Type:
        cls.check_fields(**fields)

        expression = [getattr(cls, k) == fields[k] for k in fields.keys()]

        instance = db.session.query(cls).filter(*expression).first()
        if instance:
            return instance

        raise ObjectDoesNotExist(f"No {cls.__name__.lower()} with such parameters.")

    @classmethod
    def update(cls, id, **updated_fields):
        cls.check_fields(**updated_fields)
        instance = cls.get(id=id)

        for field in updated_fields:
            setattr(instance, field, updated_fields[field])

        db.session.commit()
        db.session.refresh(instance)

        return instance

    @classmethod
    def filter(
        cls,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "created",
        desc: bool = False,
        **fields,
    ):
        cls.check_fields(**fields)

        expression = [getattr(cls, k) == fields[k] for k in fields.keys()]
        try:
            if desc:
                return (
                    db.session.query(cls)
                    .order_by(getattr(cls, order_by).desc(), cls.updated.desc())
                    .filter(*expression)
                    .offset(skip)
                    .limit(limit)
                    .all()
                )
            return (
                db.session.query(cls)
                .order_by(getattr(cls, order_by), cls.updated.desc())
                .filter(*expression)
                .offset(skip)
                .limit(limit)
                .all()
            )
        except AttributeError:
            return (
                db.session.query(cls)
                .filter(*expression)
                .offset(skip)
                .limit(limit)
                .all()
            )

    @classmethod
    def get_or_false(cls, **fields) -> Union[Type, bool]:
        try:
            instance = cls.get(**fields)
            return instance
        except ObjectDoesNotExist:
            return False

    @classmethod
    def exists(cls, **fields):
        try:
            cls.get(**fields)
            return True
        except ObjectDoesNotExist:
            return False

    @classmethod
    def _get_model_fields(cls) -> List[str]:
        fields = []

        for field in dir(cls):
            if not field.startswith("_"):
                if not callable(getattr(cls, field)) and not isinstance(
                    getattr(cls, field), MetaData
                ):  # noqa
                    fields.append(field)

        return fields

    @classmethod
    def check_fields(cls, **fields):
        for field in fields.keys():
            if field not in cls._get_model_fields():
                raise ValueError(
                    f"Field {field} is not suported, suported fields: {cls._get_model_fields()}"
                )  # noqa

    @classmethod
    def refresh(cls, instance):
        db.session.commit()
        db.session.refresh(instance)

        return instance


class BaseManagerMixin:
    @classmethod
    def manager(cls):
        return BaseManager(cls)
