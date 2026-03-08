from typing import Any

from app.api.deps import SessionDep
from app.models import Message, TaskStatus, TaskStatusesPublic, TaskStatusPublic
from fastapi import APIRouter
from sqlmodel import func, select

router = APIRouter(prefix="/task-statuses", tags=["task-statuses"])


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
