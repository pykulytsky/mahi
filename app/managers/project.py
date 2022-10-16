from .base import Manager
from app.models import Project, ProjectRead, ProjectCreate


class ProjectManager(Manager):
    model = Project
    in_schema = ProjectCreate
    read_schema = ProjectRead
