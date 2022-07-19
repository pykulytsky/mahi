from sqlalchemy import Column, DateTime

from app.db.base_class import Base
from sqlalchemy.sql import func


class Timestamped(Base):
    __abstract__ = True
    created = Column(DateTime(timezone=True), default=func.now())
    updated = Column(DateTime, onupdate=func.now())
