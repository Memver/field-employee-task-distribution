from typing import Any

from app.api.deps import SessionDep
from app.models import Message, Task, TaskPublic, TasksPublic
from fastapi import APIRouter
from sqlmodel import func, select

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get(
    "/",
    response_model=TasksPublic,
)
def read_tasks(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve tasks.
    """

    count_statement = select(func.count()).select_from(Task)
    count = session.exec(count_statement).one()

    statement = select(Task).offset(skip).limit(limit)
    tasks = session.exec(statement).all()

    return TasksPublic(data=tasks, count=count)


@router.get("/{task_id}", response_model=TaskPublic)
def read_task_by_id(task_id: int, session: SessionDep) -> Any:
    """
    Get a specific task by id.
    """
    task = session.get(Task, task_id)
    return task


@router.delete("/{task_id}")
def delete_task(session: SessionDep, task_id: int) -> Message:
    """
    Delete a task.
    """
    task = session.get(Task, task_id)
    # statement = delete(Item).where(col(Item.owner_id) == task_id)
    # session.exec(statement)
    session.delete(task)
    session.commit()
    return Message(message="Task deleted successfully")
