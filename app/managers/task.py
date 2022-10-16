from .base import Manager
from app.models import Task, TaskCreate
from .project import ProjectManager
from .section import SectionManager


class TaskManager(Manager):
    model = Task
    in_schema: TaskCreate

    def create(self, object: TaskCreate):
        parent_manager = SectionManager if object.section_id else ProjectManager
        id = object.section_id or object.project_id
        for task in parent_manager.get(id=id).tasks:
            if task.order >= object.order:
                Task.update(task.id, order=task.order + 1)
        return super().create(object=object)
