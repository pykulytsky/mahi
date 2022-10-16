from app.models import Project, ProjectCreate, ProjectRead

from .base import Manager


class ProjectManager(Manager):
    model = Project
    in_schema = ProjectCreate
    read_schema = ProjectRead
