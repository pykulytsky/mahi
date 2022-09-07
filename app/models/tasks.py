from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    event,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.types import Priority
from app.managers.base import BaseManagerMixin
from app.managers.tasks import TasksManagerMixin
from app.models.base import Timestamped


class Project(Timestamped, TasksManagerMixin):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=False, nullable=False)
    description = Column(String, unique=False, nullable=True)

    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="projects")

    is_favorite = Column(Boolean, default=False)
    is_pinned = Column(Boolean, default=False)
    is_editable = Column(Boolean, default=True)

    accent_color = Column(String, nullable=True)
    icon = Column(String, nullable=True)

    sections = relationship("Section", back_populates="project")

    sort_tasks_by = Column(String, default="is_done")
    show_completed_tasks = Column(Boolean, default=True)

    tasks = relationship("Task", back_populates="project")
    related_activities = relationship("Activity", back_populates="project")


class Section(Timestamped, TasksManagerMixin):
    id = Column(Integer, primary_key=True, index=True)
    order = Column(Integer, nullable=False)
    name = Column(String, nullable=False)

    project_id = Column(Integer, ForeignKey("project.id"))
    project = relationship("Project", back_populates="sections")

    tasks = relationship("Task", back_populates="section")


class Tag(Timestamped, TasksManagerMixin):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=False, nullable=False)
    color = Column(String, nullable=True)
    tasks = relationship("Task", secondary="tagitem", back_populates="tags")

    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="tags")
    related_activities = relationship("Activity", back_populates="tag")


class TagItem(Timestamped, BaseManagerMixin):
    id = Column(Integer, primary_key=True, index=True)
    tag_id = Column(Integer, ForeignKey("tag.id"))
    task_id = Column(Integer, ForeignKey("task.id"))


class Task(Timestamped, TasksManagerMixin):
    id = Column(Integer, primary_key=True, index=True)
    order = Column(Integer, nullable=False)

    parent_task_id = Column(Integer, ForeignKey("task.id"))
    subtasks = relationship("Task")

    name = Column(String, unique=False, nullable=False)
    description = Column(String, unique=False, nullable=True)
    deadline = Column(Date, nullable=True)
    priority = Column(Priority, nullable=True)
    is_important = Column(Boolean, default=False)
    color = Column(String, nullable=True)
    remind_at = Column(DateTime, nullable=True)

    is_done = Column(Boolean, default=False)
    done_at = Column(DateTime, nullable=True)

    tags = relationship("Tag", secondary="tagitem", back_populates="tasks")

    project_id = Column(Integer, ForeignKey("project.id"))
    project = relationship("Project", back_populates="tasks")

    section_id = Column(Integer, ForeignKey("section.id"))
    section = relationship("Section", back_populates="tasks")

    related_activities = relationship("Activity", back_populates="task")


@event.listens_for(Task.is_done, "set")
def track_task_completion(target, value, oldvalue, initiator):
    """Updates done_at field when task is being done. Is used to track productivity at dashboard."""
    if value != oldvalue:
        if value:
            target.done_at = func.now()
        else:
            target.done_at = None
