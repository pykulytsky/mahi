from app.models import Task, TaskCreate
from app.models.reaction import ReactionBase, ReactionCreate
from app.models.section import Section
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
        if object.parent_task_id:
            parent_manager = self
        elif object.section_id:
            parent_manager = SectionManager(self.session)
        else:
            parent_manager = ProjectManager(self.session)
        id = object.section_id or object.project_id or object.parent_task_id
        order = object.order if object.order else 0
        for task in parent_manager.get(id=id).tasks:
            if task.order >= order:
                self.update(task.id, order=task.order + 1)
        return super().create(object=object)

    def reorder_source(
        self,
        instance,
    ):
        if instance.parent_task_id:
            source = self.get(id=instance.parent_task_id)
        else:
            source = instance.section or instance.project
        for task in source.tasks:
            if task.order > instance.order:
                self.update(task.id, order=task.order - 1)

    def reorder_destination(self, order: int, source):
        for task in source.tasks:
            if task.order >= order:
                self.update(task.id, order=task.order + 1)

    def reorder_source_task(self, instance: Task):
        for task in instance.tasks:
            pass

    def reorder(self, instance, destination, order: int):
        self.reorder_source(instance)
        self.reorder_destination(order, destination)

        parent_task_id = None
        if isinstance(destination, Task):
            parent_task_id = destination.id
        project_id = None
        if isinstance(destination, Project):
            project_id = destination.id
        section_id = None
        if isinstance(destination, Section):
            section_id = destination.id

        return self.update(
            id=instance.id,
            order=order,
            project_id=project_id,
            section_id=section_id,
            parent_task_id=parent_task_id,
        )

    def delete(self, instance: Task):
        if instance.parent_task_id:
            model = self.get(id=instance.parent_task_id)
        else:
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

    def assign_task(self, task: Task, user: User) -> Task:
        task.assigned_to.append(user)
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        return task

    def remove_assignee(self, task: Task, user: User) -> Task:
        task.assigned_to.remove(user)
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        return task
