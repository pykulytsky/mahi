from datetime import datetime

from fastapi import BackgroundTasks, Depends, HTTPException

from app.api.deps import Permission, get_current_active_user
from app.api.router import PermissionedCrudRouter
from app.managers import ProjectManager, SectionManager, TaskManager
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
    id: int,
    project_id: int,
    user: User = Depends(get_current_active_user),
):
    task = Task.get(id=id)
    if task.project.owner == user:
        updated_task = Task.update(id=task.id, project_id=project_id)
        return updated_task
    else:
        raise HTTPException(status_code=400, detail="Authentication error")


@router.post("/{order}/reorder/", response_model=TaskRead)
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
):
    return task


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
