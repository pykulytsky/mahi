from app.models import Task, TaskCreate

from .base import Manager
from .project import ProjectManager, Project
from .section import SectionManager


class TaskManager(Manager):
    model = Task
    in_schema: TaskCreate

    def create(self, object: TaskCreate):
        parent_manager = SectionManager if object.section_id else ProjectManager
        id = object.section_id or object.project_id
        order = object.order if object.order else 0
        for task in parent_manager(self.session).get(id=id).tasks:
            if task.order >= order:
                self.update(task.id, order=task.order + 1)
        return super().create(object=object)

    def reorder_source(
        self,
        instance,
    ):
        source = instance.section or instance.project
        for task in source.tasks:
            if task.order > instance.order:
                self.update(task.id, order=task.order - 1)

    def reorder_destination(self, order: int, source):
        for task in source.tasks:
            if task.order >= order:
                self.update(task.id, order=task.order + 1)

    def reorder(self, instance, destination, order: int):
        self.reorder_source(instance)
        self.reorder_destination(order, destination)
        project_id, section_id = (
            (destination.id, None)
            if isinstance(destination, Project)
            else (None, destination.id)
        )
        return self.update(
            id=instance.id,
            order=order,
            project_id=project_id,
            section_id=section_id,
        )

    def delete(self, instance):
        model = instance.section or instance.project
        for task in model.tasks:
            if task.order > instance.order:
                self.update(task.id, order=task.order - 1)
        return super().delete(instance)
