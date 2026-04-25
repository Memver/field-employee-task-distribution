from typing import Any

from app.api.deps import AgentPointReaderUser, AgentPointTableEditorUser, SessionDep
from app.models import (
    AgentPointEvent,
    AgentPointEventCreate,
    AgentPointEventPublic,
    AgentPointEventsPublic,
    AgentPointEventUpdate,
    Message,
)
from fastapi import APIRouter, HTTPException
from sqlmodel import func, select
from app.repositories import agent_point_event as event_repository
from app.services import agent_point_event_service

router = APIRouter(prefix="/agent-point-events", tags=["agent-point-events"])


@router.post("/", response_model=AgentPointEventPublic)
def create_agent_point_event(
    *,
    session: SessionDep,
    _editor: AgentPointTableEditorUser,
    agent_point_event_in: AgentPointEventCreate,
) -> Any:
    """
    Create new agent_point_event.
    """
    return agent_point_event_service.create_event(
        session=session, payload=agent_point_event_in
    )


@router.get("/", response_model=AgentPointEventsPublic)
def read_agent_point_events(
    session: SessionDep,
    _reader: AgentPointReaderUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve agent_point_events.
    """
    count_statement = select(func.count()).select_from(AgentPointEvent)
    count = session.exec(count_statement).one()

    statement = select(AgentPointEvent).offset(skip).limit(limit)
    agent_point_events = session.exec(statement).all()

    return AgentPointEventsPublic(data=agent_point_events, count=count)


@router.get("/{agent_point_event_id}", response_model=AgentPointEventPublic)
def read_agent_point_event_by_id(
    agent_point_event_id: int, session: SessionDep, _reader: AgentPointReaderUser
) -> Any:
    """
    Get a specific agent_point_event by id.
    """
    agent_point_event = event_repository.get_by_id(
        session=session, event_id=agent_point_event_id
    )
    if not agent_point_event:
        raise HTTPException(status_code=404, detail="AgentPointEvent not found")
    return agent_point_event


@router.put("/{id}", response_model=AgentPointEventPublic)
def update_agent_point_event(
    *,
    session: SessionDep,
    _editor: AgentPointTableEditorUser,
    id: int,
    agent_point_event_in: AgentPointEventUpdate,
) -> Any:
    """
    Update an agent_point_event.
    """
    agent_point_event = event_repository.get_by_id(session=session, event_id=id)
    if not agent_point_event:
        raise HTTPException(status_code=404, detail="AgentPointEvent not found")
    return agent_point_event_service.update_event(
        session=session, event=agent_point_event, payload=agent_point_event_in
    )


@router.delete("/{agent_point_event_id}")
def delete_agent_point_event(
    session: SessionDep,
    _editor: AgentPointTableEditorUser,
    agent_point_event_id: int,
) -> Message:
    """
    Delete a agent_point_event.
    """
    agent_point_event = event_repository.get_by_id(
        session=session, event_id=agent_point_event_id
    )
    if not agent_point_event:
        raise HTTPException(status_code=404, detail="AgentPointEvent not found")
    session.delete(agent_point_event)
    session.commit()
    return Message(message="AgentPointEvent deleted successfully")
