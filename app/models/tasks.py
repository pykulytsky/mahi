from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.types import Priority
from app.managers.base import BaseManagerMixin
from app.models.base import Timestamped


class Project(Timestamped, BaseManagerMixin):
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

    sort_tasks_by = Column(String, default="is_done")

    tasks = relationship("Task", back_populates="project")


class Tag(Timestamped, BaseManagerMixin):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=False, nullable=False)
    color = Column(String, nullable=True)
    tasks = relationship("Task", secondary="tagitem", back_populates="tags")

    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="tags")


class TagItem(Timestamped, BaseManagerMixin):
    id = Column(Integer, primary_key=True, index=True)
    tag_id = Column(Integer, ForeignKey("tag.id"))
    task_id = Column(Integer, ForeignKey("task.id"))


class Task(Timestamped, BaseManagerMixin):
    id = Column(Integer, primary_key=True, index=True)

    parent_task_id = Column(Integer, ForeignKey("task.id"))
    subtasks = relationship("Task")

    name = Column(String, unique=False, nullable=False)
    description = Column(String, unique=False, nullable=True)
    deadline = Column(Date, nullable=True)
    priority = Column(Priority, nullable=True)

    is_done = Column(Boolean, default=False)
    tags = relationship("Tag", secondary="tagitem", back_populates="tasks")

    project_id = Column(Integer, ForeignKey("project.id"))
    project = relationship("Project", back_populates="tasks")
