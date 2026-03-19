from typing import Any

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Message,
    PrioritiesPublic,
    Priority,
    PriorityCreate,
    PriorityPublic,
    PriorityUpdate,
)
from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

router = APIRouter(prefix="/priorities", tags=["priorities"])


@router.post("/", response_model=PriorityPublic)
def create_priority(*, session: SessionDep, priority_in: PriorityCreate) -> Any:
    """
    Create new priority.
    """
    priority = Priority.model_validate(priority_in)
    session.add(priority)
    session.commit()
    session.refresh(priority)
    return priority


@router.get(
    "/",
    response_model=PrioritiesPublic,
)
def read_priorities(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve priorities.
    """

    count_statement = select(func.count()).select_from(Priority)
    count = session.exec(count_statement).one()

    statement = select(Priority).offset(skip).limit(limit)
    priorities = session.exec(statement).all()

    return PrioritiesPublic(data=priorities, count=count)


@router.get("/{priority_id}", response_model=PriorityPublic)
def read_priority_by_id(priority_id: int, session: SessionDep) -> Any:
    """
    Get a specific priority by id.
    """
    priority = session.get(Priority, priority_id)
    return priority


@router.put("/{id}", response_model=PriorityPublic)
def update_priority(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: int,
    priority_in: PriorityUpdate,
) -> Any:
    """
    Update an priority.
    """
    priority = session.get(Priority, id)
    if not priority:
        raise HTTPException(status_code=404, detail="Priority not found")
    update_dict = priority_in.model_dump(exclude_unset=True)
    priority.sqlmodel_update(update_dict)
    session.add(priority)
    session.commit()
    session.refresh(priority)
    return priority


@router.delete("/{priority_id}")
def delete_priority(session: SessionDep, priority_id: int) -> Message:
    """
    Delete a priority.
    """
    priority = session.get(Priority, priority_id)
    # statement = delete(Item).where(col(Item.owner_id) == priority_id)
    # session.exec(statement)
    session.delete(priority)
    session.commit()
    return Message(message="Priority deleted successfully")
