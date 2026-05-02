from typing import Any

from app.api.deps import EmployeeManagerUser, ManagerOrFieldEmployeeUser, SessionDep
from app.models import (
    Message,
    TaskType,
    TaskTypeCreate,
    TaskTypePublic,
    TaskTypesPublic,
    TaskTypeUpdate,
)
from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

router = APIRouter(prefix="/task-types", tags=["task-types"])


@router.post("/", response_model=TaskTypePublic)
def create_task_type(
    *, session: SessionDep, _em: EmployeeManagerUser, task_type_in: TaskTypeCreate
) -> Any:
    """
    Create new task_type.
    """
    task_type = TaskType.model_validate(task_type_in)
    session.add(task_type)
    session.commit()
    session.refresh(task_type)
    return task_type


@router.get(
    "/",
    response_model=TaskTypesPublic,
)
def read_task_types(
    session: SessionDep, _reader: ManagerOrFieldEmployeeUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve task_types.
    """

    count_statement = select(func.count()).select_from(TaskType)
    count = session.exec(count_statement).one()

    statement = select(TaskType).offset(skip).limit(limit)
    task_types = session.exec(statement).all()

    return TaskTypesPublic(data=task_types, count=count)


@router.get("/{task_type_id}", response_model=TaskTypePublic)
def read_task_type_by_id(
    task_type_id: int, session: SessionDep, _reader: ManagerOrFieldEmployeeUser
) -> Any:
    """
    Get a specific task_type by id.
    """
    task_type = session.get(TaskType, task_type_id)
    return task_type


@router.put("/{id}", response_model=TaskTypePublic)
def update_task_type(
    *,
    session: SessionDep,
    _em: EmployeeManagerUser,
    id: int,
    task_type_in: TaskTypeUpdate,
) -> Any:
    """
    Update an task_type.
    """
    task_type = session.get(TaskType, id)
    if not task_type:
        raise HTTPException(status_code=404, detail="TaskType not found")
    update_dict = task_type_in.model_dump(exclude_unset=True)
    task_type.sqlmodel_update(update_dict)
    session.add(task_type)
    session.commit()
    session.refresh(task_type)
    return task_type


@router.delete("/{task_type_id}")
def delete_task_type(
    session: SessionDep, _em: EmployeeManagerUser, task_type_id: int
) -> Message:
    """
    Delete a task_type.
    """
    task_type = session.get(TaskType, task_type_id)
    # statement = delete(Item).where(col(Item.owner_id) == task_type_id)
    # session.exec(statement)
    session.delete(task_type)
    session.commit()
    return Message(message="TaskType deleted successfully")
