from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func

from app.db.base_class import Base


class Timestamped(Base):
    __abstract__ = True
    created = Column(DateTime(timezone=True), default=func.now())
    updated = Column(DateTime, onupdate=func.now(), default=func.now())

    __mapper_args__ = {"eager_defaults": True}
