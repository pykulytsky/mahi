from app.models import Section, SectionCreate, SectionRead

from .base import Manager


class SectionManager(Manager):
    model = Section
    in_schema = SectionCreate
    read_schema = SectionRead
