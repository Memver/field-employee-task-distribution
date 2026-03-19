from typing import Any

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Message,
    TaskStatus,
    TaskStatusCreate,
    TaskStatusesPublic,
    TaskStatusPublic,
    TaskStatusUpdate,
)
from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

router = APIRouter(prefix="/task-statuses", tags=["task-statuses"])


@router.post("/", response_model=TaskStatusPublic)
def create_task_status(*, session: SessionDep, task_status_in: TaskStatusCreate) -> Any:
    """
    Create new task_status.
    """
    task_status = TaskStatus.model_validate(task_status_in)
    session.add(task_status)
    session.commit()
    session.refresh(task_status)
    return task_status


@router.get(
    "/",
    response_model=TaskStatusesPublic,
)
def read_task_statuses(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve task_statuses.
    """

    count_statement = select(func.count()).select_from(TaskStatus)
    count = session.exec(count_statement).one()

    statement = select(TaskStatus).offset(skip).limit(limit)
    task_statuses = session.exec(statement).all()

    return TaskStatusesPublic(data=task_statuses, count=count)


@router.get("/{task_status_id}", response_model=TaskStatusPublic)
def read_task_status_by_id(task_status_id: int, session: SessionDep) -> Any:
    """
    Get a specific task_status by id.
    """
    task_status = session.get(TaskStatus, task_status_id)
    return task_status


@router.put("/{id}", response_model=TaskStatusPublic)
def update_task_status(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: int,
    task_status_in: TaskStatusUpdate,
) -> Any:
    """
    Update an task_status.
    """
    task_status = session.get(TaskStatus, id)
    if not task_status:
        raise HTTPException(status_code=404, detail="TaskStatus not found")
    update_dict = task_status_in.model_dump(exclude_unset=True)
    task_status.sqlmodel_update(update_dict)
    session.add(task_status)
    session.commit()
    session.refresh(task_status)
    return task_status


@router.delete("/{task_status_id}")
def delete_task_status(session: SessionDep, task_status_id: int) -> Message:
    """
    Delete a task_status.
    """
    task_status = session.get(TaskStatus, task_status_id)
    # statement = delete(Item).where(col(Item.owner_id) == task_status_id)
    # session.exec(statement)
    session.delete(task_status)
    session.commit()
    return Message(message="TaskStatus deleted successfully")
