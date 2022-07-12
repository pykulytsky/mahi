from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(settings.SQLALCHEMY_TEST_DATABASE_URI)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
