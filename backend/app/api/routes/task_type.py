from typing import Any

from app.api.deps import SessionDep
from app.models import Message, TaskType, TaskTypePublic, TaskTypesPublic
from fastapi import APIRouter
from sqlmodel import func, select

router = APIRouter(prefix="/task-types", tags=["task-types"])


@router.get(
    "/",
    response_model=TaskTypesPublic,
)
def read_task_types(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve task_types.
    """

    count_statement = select(func.count()).select_from(TaskType)
    count = session.exec(count_statement).one()

    statement = select(TaskType).offset(skip).limit(limit)
    task_types = session.exec(statement).all()

    return TaskTypesPublic(data=task_types, count=count)


@router.get("/{task_type_id}", response_model=TaskTypePublic)
def read_task_type_by_id(task_type_id: int, session: SessionDep) -> Any:
    """
    Get a specific task_type by id.
    """
    task_type = session.get(TaskType, task_type_id)
    return task_type


@router.delete("/{task_type_id}")
def delete_task_type(session: SessionDep, task_type_id: int) -> Message:
    """
    Delete a task_type.
    """
    task_type = session.get(TaskType, task_type_id)
    # statement = delete(Item).where(col(Item.owner_id) == task_type_id)
    # session.exec(statement)
    session.delete(task_type)
    session.commit()
    return Message(message="TaskType deleted successfully")
