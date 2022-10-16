from .base import Manager
from app.models import Section, SectionCreate, SectionRead


class SectionManager(Manager):
    model = Section
    in_schema = SectionCreate
    read_schema = SectionRead
