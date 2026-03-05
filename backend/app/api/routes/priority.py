from typing import Any

from app.api.deps import SessionDep
from app.models import Message, PrioritiesPublic, Priority, PriorityPublic
from fastapi import APIRouter
from sqlmodel import func, select

router = APIRouter(prefix="/priorities", tags=["priorities"])


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
