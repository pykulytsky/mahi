from typing import Type

from sqlmodel import SQLModel


class NotValidModel(Exception):
    pass


class ObjectDoesNotExist(Exception):
    def __init__(self, model: Type[SQLModel], id: int | None = None) -> None:
        self.model = model
        self.id = id
        self.message = (
            f"No {self.model.__name__} with given id({id}) was found."  # noqa:501
        )
        super().__init__(self.message)


class ImproperlyConfigured(Exception):
    pass
