from app.models import tasks, user
from .base import BaseManager, BaseManagerMixin


class TasksBaseManager(BaseManager):
    @classmethod
    def create(cls, disable_check: bool = False, **fields):
        instance = super().create(disable_check, **fields)
        # self.handle_activity(instance, "created")

        return instance

    @classmethod
    def delete(cls, instance):
        # self.handle_activity(instance, "deleted")
        return super().delete(instance)

    @classmethod
    def update(cls, id, **updated_fields):
        # self.handle_activity(self.get(id=id), "updated")
        return super().update(id, **updated_fields)

    def handle_activity(cls, instance, action: str) -> user.Activity:
        actor = None
        if isinstance(instance, tasks.Task):
            if instance.project:
                actor = instance.project.owner
        elif isinstance(instance, tasks.TagItem):
            actor = tasks.Tag.get(id=instance.tag_id).owner
        else:
            actor = instance.owner
        try:
            if not actor.journal:
                user.ActivityJournal.create(user=actor)
        except AttributeError:
            user.ActivityJournal.create(user=actor)

        target = {cls.__name__.lower(): instance}
        try:
            return user.Activity.create(
                journal=actor.journal, actor=actor, action=action, **target
            )
        except AttributeError:
            return user.Activity.create(
                actor=actor, action=action, **target
            )


class TasksManager(TasksBaseManager):
    @classmethod
    def create(cls, disable_check: bool = False, **fields):
        model = tasks.Section if fields.get("section_id", False) else tasks.Project
        id = (
            fields["section_id"]
            if fields.get("section_id", False)
            else fields["project_id"]
        )
        fields["order"] = fields["order"] if fields.get("order", False) else 0
        for task in model.get(id=id).tasks:
            if task.order >= fields["order"]:
                tasks.Task.update(task.id, order=task.order + 1)
        return super().create(disable_check, **fields)

    @classmethod
    def delete(cls, instance):
        model = instance.section or instance.project
        for task in model.tasks:
            if task.order > instance.order:
                tasks.Task.update(task.id, order=task.order - 1)
        return super().delete(instance)

    @classmethod
    def reorder_source(
        cls,
        instance,
    ):
        source = instance.section or instance.project
        for task in source.tasks:
            if task.order > instance.order:
                tasks.Task.update(
                    task.id,
                    order=task.order - 1
                )

    @classmethod
    def reorder_destination(
        cls,
        order: int,
        source
    ):
        for task in source.tasks:
            if task.order >= order:
                tasks.Task.update(
                    task.id,
                    order=task.order + 1
                )

    @classmethod
    def reorder(
        cls,
        instance,
        destination,
        order: int
    ):
        cls.reorder_source(instance)
        cls.reorder_destination(order, destination)
        project_id, section_id = (destination.id, None) if isinstance(destination, tasks.Project) else (None, destination.id)
        return tasks.Task.update(
            id=instance.id,
            order=order,
            project_id=project_id,
            section_id=section_id,
        )


class SectionManager(TasksBaseManager):
    @classmethod
    def create(cls, disable_check: bool = False, **fields):
        fields["order"] = fields["order"] if fields.get("order", False) else 0
        for section in tasks.Project.get(id=fields["project_id"]).sections:
            if section.order >= fields["order"]:
                tasks.Section.update(id=section.id, order=section.order + 1)
        return super().create(disable_check, **fields)

    @classmethod
    def delete(cls, instance):
        for section in instance.project.sections:
            if section.order > instance.order:
                tasks.Section.update(id=section.id, order=section.order - 1)
        return super().delete(instance)

    @classmethod
    def reorder(cls, instance, destination, order: int):
        fields = instance.__dict__.copy()
        fields.pop("_sa_instance_state")
        fields["order"] = order
        tasks.Section.manager.delete(instance)
        return tasks.Section.manager.create(**fields)


class TasksBaseManagerMixin(BaseManagerMixin):
    @classmethod
    def manager(cls):
        return TasksBaseManager(cls)


class TasksManagerMixin(BaseManagerMixin):
    @classmethod
    def manager(cls):
        return TasksManager(cls)


class SectionsManagerMixin(BaseManagerMixin):
    @classmethod
    def manager(cls):
        return SectionManager(cls)
