from app.models import tasks, user

from .base import BaseManager, BaseManagerMixin


class TasksManager(BaseManager):
    def create(self, disable_check: bool = False, **fields):
        instance = super().create(disable_check, **fields)
        self.handle_activity(instance, "created")

        return instance

    def delete(self, instance):
        self.handle_activity(instance, "deleted")
        return super().delete(instance)

    def update(self, id, **updated_fields):
        self.handle_activity(self.get(id=id), "updated")
        return super().update(id, **updated_fields)

    def handle_activity(self, instance, action: str) -> user.Activity:
        actor = None
        if isinstance(instance, tasks.Task):
            actor = instance.project.owner
        elif isinstance(instance, tasks.TagItem):
            actor = tasks.Tag.manager(self.db).get(id=instance.tag_id).owner
        else:
            actor = instance.owner

        if not actor.journal:
            user.ActivityJournal.manager(self.db).create(user=actor)

        target = {self.model.__name__.lower(): instance}
        return user.Activity.manager(self.db).create(
            journal=actor.journal, actor=actor, action=action, **target
        )


class TasksManagerMixin(BaseManagerMixin):
    @classmethod
    def manager(cls, db):
        return TasksManager(cls, db)
