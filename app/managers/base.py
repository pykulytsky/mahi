from typing import List, Type

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.exceptions import ImproperlyConfigured, ObjectDoesNotExists
from app.db.base_class import Base


class BaseManager:
    def __init__(self, klass: Type, db: AsyncSession) -> None:
        if not issubclass(klass, Base):
            raise ImproperlyConfigured(f"Type {klass.__name__} is not suported.")

        self.model = klass
        self.db = db

    async def create(self, disable_check: bool = False, **fields):
        if not disable_check:
            self.check_fields(**fields)
        instance = self.model(**fields)

        self.db.add(instance)
        self.db.commit()
        await self.db.refresh(instance)

        return instance

    def delete(self, instance):
        if not isinstance(instance, self.model):
            raise TypeError(f"Instance must be {str(self.model)} not {type(instance)}")
        self.db.delete(instance)
        self.db.commit()

    async def all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "created",
        desc: bool = False,
    ):
        try:
            if desc:
                result = await self.db.execute(
                    select(self.model)
                    .order_by(getattr(self.model, order_by).desc())
                    .offset(skip)
                    .limit(limit)
                )

                return result.scalars().all()

            result = await self.db.execute(
                select(self.model)
                .order_by(getattr(self.model, order_by))
                .offset(skip)
                .limit(limit)
            )

            return result.scalars().all()
        except AttributeError:
            result = await self.db.execute(select(self.model).offset(skip).limit(limit))
            return result.scalars().all()

    async def get(self, **fields) -> Type:
        self.check_fields(**fields)

        expression = [getattr(self.model, k) == fields[k] for k in fields.keys()]

        result = await self.db.execute(select(self.model).filter(*expression))
        instance = result.scalars().first()
        if instance:
            return instance

        raise ObjectDoesNotExists(
            f"No {self.model.__name__.lower()} with such parameters."
        )

    async def update(self, id, **updated_fields):
        self.check_fields(**updated_fields)
        instance = await self.get(id=id)

        for field in updated_fields:
            setattr(instance, field, updated_fields[field])

        self.db.commit()
        self.db.refresh(instance)

        return instance

    async def filter(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "created",
        desc: bool = False,
        **fields,
    ):
        self.check_fields(**fields)

        expression = [getattr(self.model, k) == fields[k] for k in fields.keys()]
        try:
            if desc:
                result = await self.db.execute(
                    select(self.model)
                    .order_by(
                        getattr(self.model, order_by).desc(), self.model.updated.desc()
                    )
                    .filter(*expression)
                    .offset(skip)
                    .limit(limit)
                )

                return result.scalars.all()

            result = await self.db.execute(
                select(self.model)
                .order_by(getattr(self.model, order_by), self.model.updated.desc())
                .filter(*expression)
                .offset(skip)
                .limit(limit)
            )

            return result.scalars.all()
        except AttributeError:
            result = await self.db.execute(
                select(self.model)
                .filter(*expression)
                .offset(skip)
                .limit(limit)
            )

            return result.scalars().all()

    async def get_or_false(self, **fields):
        try:
            instance = await self.get(**fields)
            return instance
        except ObjectDoesNotExists:
            return False

    async def exists(self, **fields):
        try:
            await self.get(**fields)
            return True
        except ObjectDoesNotExists:
            return False

    def _get_model_fields(self) -> List[str]:
        fields = []

        for field in dir(self.model):
            if not field.startswith("_"):
                if not callable(getattr(self.model, field)) and not isinstance(
                    getattr(self.model, field), MetaData
                ):  # noqa
                    fields.append(field)

        return fields

    def check_fields(self, **fields):
        for field in fields.keys():
            if field not in self._get_model_fields():
                raise ValueError(
                    f"Field {field} is not suported, suported fields: {self._get_model_fields()}"
                )  # noqa

    async def refresh(self, instance):
        self.db.commit()
        await self.db.refresh(instance)

        return instance


class BaseManagerMixin:
    @classmethod
    def manager(cls, db):
        return BaseManager(cls, db)
