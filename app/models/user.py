import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from app.managers.base import BaseManagerMixin
from app.managers.users import UserManagerMixin
from app.models.base import Timestamped


class User(Timestamped, UserManagerMixin):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    avatar = Column(String, nullable=True)

    verification_code = Column(UUID(as_uuid=True), default=uuid.uuid4())
    email_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)

    projects = relationship("Project", back_populates="owner")
    tags = relationship("Tag", back_populates="owner")

    tasks_goal_per_day = Column(Integer, default=5)

    journal = relationship("ActivityJournal", back_populates="user", uselist=False)
    activities = relationship("Activity", back_populates="actor")
    messages = relationship("Message", back_populates="user")

    @hybrid_property
    def full_name(self) -> str:
        return self.first_name + " " + self.last_name


class ActivityJournal(Timestamped, BaseManagerMixin):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="journal")

    activities = relationship("Activity", back_populates="journal")


class Activity(Timestamped, BaseManagerMixin):
    id = Column(Integer, primary_key=True, index=True)

    journal_id = Column(Integer, ForeignKey("activityjournal.id"))
    journal = relationship("ActivityJournal", back_populates="activities")

    actor_id = Column(Integer, ForeignKey("user.id"))
    actor = relationship("User", back_populates="activities")

    action = Column(String)

    project_id = Column(Integer, ForeignKey("project.id"))
    project = relationship("Project", back_populates="related_activities")
    task_id = Column(Integer, ForeignKey("task.id"))
    task = relationship("Task", back_populates="related_activities")
    tag_id = Column(Integer, ForeignKey("tag.id"))
    tag = relationship("Tag", back_populates="related_activities")

    @hybrid_property
    def target(self):
        if self.project:
            return self.project
        if self.tag:
            return self.tag
        if self.task:
            return self.task

    # @hybrid_property
    # def target_type(self):
    #     if self.project:
    #         return "project"
    #     if self.task:
    #         return "task"
    #     if self.task:
    #         return "task"

    @hybrid_property
    def summary(self) -> str | None:
        if self.target:
            return f"{self.actor} {self.action} {self.target}"


class Message(Timestamped, BaseManagerMixin):
    id = Column(Integer, primary_key=True, index=True)

    published = Column(Boolean, default=False)
    read = Column(Boolean, default=False)

    channel = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="messages")

    body = Column(String, nullable=False)
