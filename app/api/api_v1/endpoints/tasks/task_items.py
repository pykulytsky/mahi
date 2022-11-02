from datetime import datetime

from fastapi import BackgroundTasks, Depends, HTTPException

from app.api.deps import Permission, get_current_active_user
from app.api.router import PermissionedCrudRouter
from app.managers import ProjectManager, SectionManager, TaskManager
from app.managers.tag import TagManager
from app.managers.user import UserManager
from app.models import (
    Project,
    ReactionBase,
    Task,
    TaskCreate,
    TaskRead,
    TaskReadDetail,
    TaskReorder,
    TaskUpdate,
    User,
)
from app.models.task import Reorder
from app.sse.tasks import deadline_remind, remind

router = PermissionedCrudRouter(
    model=Task,
    manager=TaskManager,
    get_schema=TaskRead,
    create_schema=TaskCreate,
    update_schema=TaskUpdate,
    detail_schema=TaskReadDetail,
    prefix="/tasks",
    tags=["task"],
    owner_field_is_required=True,
)


@router.post("/", response_model=TaskReadDetail)
async def create_task(
    task_in: TaskCreate,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_active_user),
    manager: TaskManager = Depends(TaskManager),
):
    task_in.owner_id = user.id
    instance = manager.create(task_in)
    if task_in.remind_at is not None:
        background_tasks.add_task(remind, instance)
    if task_in.deadline is not None:
        background_tasks.add_task(deadline_remind, instance)
    return instance


@router.get("/date/{date}", response_model=list[TaskReadDetail])
async def get_tasks_by_date(
    date: str,
    user: User = Depends(get_current_active_user),
    manager: ProjectManager = Depends(ProjectManager),
    tasks_manager: TaskManager = Depends(TaskManager),
):
    raw_date = datetime.strptime(date, "%Y-%m-%d")
    owned_projects = manager.filter(Project.owner_id == user.id)
    tasks = []
    for project in owned_projects:
        tasks += tasks_manager.filter(
            Task.deadline == raw_date, Task.project_id == project.id
        )
    return tasks


@router.post("/{id}/move/{project_id}", response_model=TaskRead)
async def move_task_to_proejct(
    project_id: int,
    user: User = Depends(get_current_active_user),
    task: Task = Permission("edit", router._get_item()),
    manager: TaskManager = Depends(TaskManager),
):
    if task.project.owner == user:
        updated_task = manager.update(id=task.id, project_id=project_id)
        return updated_task
    else:
        raise HTTPException(status_code=400, detail="Authentication error")


@router.post("/{order}/reorder/v2", response_model=TaskRead)
async def reorder_tasks(
    order: str | int,
    reorder_schema: TaskReorder,
    manager: TaskManager = Depends(TaskManager),
    section_manager: SectionManager = Depends(SectionManager),
    project_manager: ProjectManager = Depends(ProjectManager),
):

    project_id, section_id = (
        (reorder_schema.source_id, None)
        if reorder_schema.source_type == "project"
        else (None, reorder_schema.source_id)
    )
    instance = manager.one(
        Task.section_id == section_id,
        Task.project_id == project_id,
        Task.order == order,
    )

    parent_manager = (
        section_manager
        if reorder_schema.destination_type == "section"
        else project_manager
    )
    destination = parent_manager.get(id=reorder_schema.destination_id)

    return manager.reorder(instance, destination, reorder_schema.order)


@router.post("/{id}/assign/{user_id}", response_model=TaskReadDetail)
async def assign_task(
    user_id: int,
    task: Task = Permission("edit", router._get_item()),
    user_manager: UserManager = Depends(UserManager),
    manager: TaskManager = Depends(TaskManager),
):
    assignee = user_manager.get(id=user_id)
    if assignee in task.assigned_to:
        raise HTTPException(
            status_code=400, detail="User is already assigned to this task"
        )
    return manager.assign_task(task, assignee)


@router.post("/{id}/assign/{user_id}/remove", response_model=TaskReadDetail)
async def remove_assign(
    user_id: int,
    task: Task = Permission("edit", router._get_item()),
    user_manager: UserManager = Depends(UserManager),
    manager: TaskManager = Depends(TaskManager),
):
    assignee = user_manager.get(id=user_id)
    if assignee not in task.assigned_to:
        raise HTTPException(status_code=400, detail="User is not assigned to this task")
    return manager.remove_assignee(task, assignee)


@router.post("/{id}/reactions", response_model=TaskReadDetail)
async def add_reaction(
    reaction: ReactionBase,
    user: User = Depends(get_current_active_user),
    task: Task = Permission("edit", router._get_item()),
    task_manager: TaskManager = Depends(TaskManager),
):
    return task_manager.add_reaction(reaction, task, user)


@router.post("/{id}/reactions/remove", response_model=TaskReadDetail)
async def remove_reaction(
    reaction: ReactionBase,
    user: User = Depends(get_current_active_user),
    task: Task = Permission("edit", router._get_item()),
    task_manager: TaskManager = Depends(TaskManager),
):
    try:
        task = task_manager.remove_reaction(reaction, task, user)
        return task
    except:  # noqa
        raise HTTPException(status_code=404, detail="No reactions was found")


@router.post("/{id}/tags/{tag_id}", response_model=TaskReadDetail)
async def apply_tag(
    tag_id: int,
    task: Task = Permission("edit", router._get_item()),
    task_manager: TaskManager = Depends(TaskManager),
    tag_manager: TagManager = Depends(TagManager),
):
    tag = tag_manager.get(id=tag_id)
    if tag in task.tags:
        raise HTTPException(
            status_code=400,
            detail=f"Tag with id {tag.id} was already applied to this task",
        )
    return task_manager.apply_tag(tag, task)


@router.post("/{id}/tags/{tag_id}/remove", response_model=TaskReadDetail)
async def remove_tag(
    tag_id: int,
    task: Task = Permission("edit", router._get_item()),
    task_manager: TaskManager = Depends(TaskManager),
    tag_manager: TagManager = Depends(TagManager),
):
    tag = tag_manager.get(id=tag_id)
    if tag not in task.tags:
        raise HTTPException(
            status_code=400, detail=f"Tag with id {tag.id} is not applied to this task"
        )
    return task_manager.remove_tag(tag, task)


@router.post("/{id}/reorder", response_model=Task)
async def reorder(
    in_data: Reorder,
    task: Task = Permission("edit", router._get_item()),
    manager: TaskManager = Depends(TaskManager),
    project_manager: ProjectManager = Depends(ProjectManager),
    section_manager: SectionManager = Depends(SectionManager)
):
    if in_data.container_type == "root":
        destination = project_manager.get(id=in_data.container_id)
    elif in_data.container_type == "task":
        destination = manager.get(id=in_data.container_id)
    else:
        destination = section_manager.get(id=in_data.container_id)
    return manager.reorder(task, destination, in_data.order)
