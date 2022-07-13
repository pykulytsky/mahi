from app.models.base import Timestamped
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.managers.base import BaseManagerMixin


class Project(Timestamped, BaseManagerMixin):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=False, nullable=False)
    description = Column(String, unique=False, nullable=True)

    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="projects")

    is_favorite = Column(Boolean, default=False)
    is_pinned = Column(Boolean, default=False)
    accent_color = Column(String, nullable=True)
    icon = Column(String, nullable=True)

    todos = relationship("TodoItem", back_populates="project")


class Tag(Timestamped, BaseManagerMixin):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=False, nullable=False)
    color = Column(String, nullable=True)
    todo_items = relationship('TodoItem', secondary='tagitem', back_populates='tags')


class TagItem(Timestamped):
    id = Column(Integer, primary_key=True, index=True)
    tag_id = Column(Integer, ForeignKey("tag.id"))
    todo_item_id = Column(Integer, ForeignKey("todoitem.id"))


class TodoItem(Timestamped, BaseManagerMixin):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=False, nullable=False)
    description = Column(String, unique=False, nullable=True)
    deadline = Column(Date, nullable=True)

    is_done = Column(Boolean, default=False)
    tags = relationship("Tag", secondary="tagitem", back_populates="todo_items")

    project_id = Column(Integer, ForeignKey("project.id"))
    project = relationship("Project", back_populates="todos")
