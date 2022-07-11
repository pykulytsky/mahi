from src.db.base_class import Base
import uuid

from sqlalchemy import Integer, Column, String, Boolean


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)

    verification_code = Column(uuid.UUID(as_uuid=True), default=uuid.uuid4())
    email_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
