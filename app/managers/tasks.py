from app.models import tasks, user
from .base import BaseManager, BaseManagerMixin


class TasksBaseManager(BaseManager):
    def create(self, disable_check: bool = False, **fields):
        instance = super().create(disable_check, **fields)
        # self.handle_activity(instance, "created")

        return instance

    def delete(self, instance):
        # self.handle_activity(instance, "deleted")
        return super().delete(instance)

    async def update(self, id, **updated_fields):
        # self.handle_activity(self.get(id=id), "updated")
        return await super().update(id, **updated_fields)

    async def handle_activity(self, instance, action: str) -> user.Activity:
        actor = None
        if isinstance(instance, tasks.Task):
            if instance.project:
                actor = instance.project.owner
        elif isinstance(instance, tasks.TagItem):
            actor = await tasks.Tag.manager(self.db).get(id=instance.tag_id).owner
        else:
            actor = instance.owner
        try:
            if not actor.journal:
                user.ActivityJournal.manager(self.db).create(user=actor)
        except AttributeError:
            user.ActivityJournal.manager(self.db).create(user=actor)

        target = {self.model.__name__.lower(): instance}
        try:
            return user.Activity.manager(self.db).create(
                journal=actor.journal, actor=actor, action=action, **target
            )
        except AttributeError:
            return user.Activity.manager(self.db).create(
                actor=actor, action=action, **target
            )


class TasksManager(TasksBaseManager):
    async def create(self, disable_check: bool = False, **fields):
        model = tasks.Section if fields.get("section_id", False) else tasks.Project
        id = (
            fields["section_id"]
            if fields.get("section_id", False)
            else fields["project_id"]
        )
        fields["order"] = fields["order"] if fields.get("order", False) else 0
        for task in await model.manager(self.db).get(id=id).tasks:
            if task.order >= fields["order"]:
                await tasks.Task.manager(self.db).update(task.id, order=task.order + 1)
        return await super().create(disable_check, **fields)

    async def delete(self, instance):
        model = instance.section or instance.project
        for task in model.tasks:
            if task.order > instance.order:
                await tasks.Task.manager(self.db).update(task.id, order=task.order - 1)
        return super().delete(instance)

    async def reorder_source(
        self,
        instance,
    ):
        source = instance.section or instance.project
        for task in source.tasks:
            if task.order > instance.order:
                await tasks.Task.manager(self.db).update(
                    task.id,
                    order=task.order - 1
                )

    async def reorder_destination(
        self,
        order: int,
        source
    ):
        for task in source.tasks:
            if task.order >= order:
                await tasks.Task.manager(self.db).update(
                    task.id,
                    order=task.order + 1
                )

    async def reorder(
        self,
        instance,
        destination,
        order: int
    ):
        await self.reorder_source(instance)
        await self.reorder_destination(order, destination)
        project_id, section_id = (destination.id, None) if isinstance(destination, tasks.Project) else (None, destination.id)
        return await tasks.Task.manager(self.db).update(
            id=instance.id,
            order=order,
            project_id=project_id,
            section_id=section_id,
        )


class SectionManager(TasksBaseManager):
    async def create(self, disable_check: bool = False, **fields):
        fields["order"] = fields["order"] if fields.get("order", False) else 0
        for section in await tasks.Project.manager(self.db).get(id=fields["project_id"]).sections:
            if section.order >= fields["order"]:
                await tasks.Section.manager(self.db).update(id=section.id, order=section.order + 1)
        return super().create(disable_check, **fields)

    async def delete(self, instance):
        for section in instance.project.sections:
            if section.order > instance.order:
                await tasks.Section.manager(self.db).update(id=section.id, order=section.order - 1)
        return super().delete(instance)

    async def reorder(self, instance, destination, order: int):
        fields = instance.__dict__.copy()
        fields.pop("_sa_instance_state")
        fields["order"] = order
        await self.delete(instance)
        return tasks.Section.manager(self.db).create(**fields)


class TasksBaseManagerMixin(BaseManagerMixin):
    @classmethod
    def manager(cls, db):
        return TasksBaseManager(cls, db)


class TasksManagerMixin(BaseManagerMixin):
    @classmethod
    def manager(cls, db):
        return TasksManager(cls, db)


class SectionsManagerMixin(BaseManagerMixin):
    @classmethod
    def manager(cls, db):
        return SectionManager(cls, db)
