from .tasks import TaskBase


class SubtaskBase(TaskBase):
    parent_task_id: int


class SubtaskCreate(SubtaskBase):
    name: str
    project_id: int


class SubtaskUpdate(SubtaskBase):
    is_done: bool | None = True
