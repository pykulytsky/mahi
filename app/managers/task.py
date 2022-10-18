from app.models import Task, TaskCreate
from app.models.reaction import ReactionBase, ReactionCreate
from app.models.tag import Tag
from app.models.user import User

from .base import Manager
from .project import Project, ProjectManager
from .reaction import ReactionManager
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

    def add_reaction(self, reaction: ReactionBase, task: Task, user: User):
        for r in task.reactions:
            if reaction.emoji == r.emoji:
                r.users.append(user)
                self.session.add(r)
                self.session.commit()
                self.session.refresh(r)
                return task

        reaction = ReactionManager(self.session).create(
            ReactionCreate(emoji=reaction.emoji, task_id=task.id)
        )
        reaction.users.append(user)
        self.session.add(reaction)
        self.session.commit()
        self.session.refresh(task)
        return task

    def remove_reaction(self, reaction: ReactionBase, task: Task, user: User):
        for r in task.reactions:
            if reaction.emoji == r.emoji:
                r.users.remove(user)
                if len(r.users) == 0:
                    ReactionManager(self.session).delete(r)
                self.session.commit()
                self.session.refresh(task)
        return task

    def apply_tag(self, tag: Tag, task: Task) -> Task:
        task.tags.append(tag)
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        return task

    def remove_tag(self, tag: Tag, task: Task) -> Task:
        task.tags.remove(tag)
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        return task

