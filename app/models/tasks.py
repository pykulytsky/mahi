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
from app.managers.base import BaseManager
from app.managers.tasks import SectionManager, TasksBaseManager, TasksManager
from app.models.base import Timestamped


class Participant(Timestamped):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    project_id = Column(Integer, ForeignKey("project.id"))


class Project(Timestamped, TasksBaseManager):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=False, nullable=False)
    description = Column(String, unique=False, nullable=True)

    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="projects")

    participants = relationship(
        "User", secondary="participant", back_populates="participated_projects"
    )

    is_favorite = Column(Boolean, default=False)
    is_pinned = Column(Boolean, default=False)
    is_editable = Column(Boolean, default=True)

    deadline = Column(Date, nullable=True)

    accent_color = Column(String, nullable=True)
    icon = Column(String, nullable=True)

    sections = relationship(
        "Section", back_populates="project", order_by="app.models.tasks.Section.order"
    )

    sort_tasks_by = Column(String, default="is_done")
    show_completed_tasks = Column(Boolean, default=True)

    tasks = relationship(
        "Task",
        back_populates="project",
        order_by="app.models.tasks.Task.is_done, app.models.tasks.Task.order",
    )
    related_activities = relationship("Activity", back_populates="project")


class Section(Timestamped, SectionManager):
    id = Column(Integer, primary_key=True, index=True)
    order = Column(Integer, nullable=False)
    name = Column(String, nullable=False)

    project_id = Column(Integer, ForeignKey("project.id"))
    project = relationship("Project", back_populates="sections")

    is_collapsed = Column(Boolean, default=False)

    tasks = relationship(
        "Task",
        back_populates="section",
        order_by="app.models.tasks.Task.is_done, app.models.tasks.Task.order",
    )


class Tag(Timestamped, TasksBaseManager):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=False, nullable=False)
    color = Column(String, nullable=True)
    tasks = relationship("Task", secondary="tagitem", back_populates="tags")

    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="tags")
    related_activities = relationship("Activity", back_populates="tag")


class TagItem(Timestamped, BaseManager):
    id = Column(Integer, primary_key=True, index=True)
    tag_id = Column(Integer, ForeignKey("tag.id"))
    task_id = Column(Integer, ForeignKey("task.id"))


class Task(Timestamped, TasksManager):
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

    reactions = relationship("Reaction", back_populates="task")


@event.listens_for(Task.is_done, "set")
def track_task_completion(target, value, oldvalue, initiator):
    """Updates done_at field when task is being done. Is used to track productivity at dashboard."""
    if value != oldvalue:
        if value:
            target.done_at = func.now()
        else:
            target.done_at = None


class UserReaction(Timestamped, BaseManager):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    reaction_id = Column(Integer, ForeignKey("reaction.id"))


class Reaction(Timestamped, BaseManager):
    id = Column(Integer, primary_key=True, index=True)
    emoji = Column(String, nullable=False)

    task_id = Column(Integer, ForeignKey("task.id"))
    task = relationship("Task", back_populates="reactions")

    users = relationship("User", secondary="userreaction", back_populates="reactions")
