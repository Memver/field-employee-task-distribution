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
from app.services.agent_point_event_schema import validate_agent_point_event_payload

router = APIRouter(prefix="/agent-point-events", tags=["agent-point-events"])


def ensure_event_schema_or_422(
    agent_point_event_in: AgentPointEventCreate | AgentPointEventUpdate,
) -> None:
    try:
        validate_agent_point_event_payload(
            event_type=agent_point_event_in.event_type,
            metric_name=agent_point_event_in.metric_name,
            metric_delta=agent_point_event_in.metric_delta,
            metric_value_num=agent_point_event_in.metric_value_num,
            metric_value_bool=agent_point_event_in.metric_value_bool,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


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
    ensure_event_schema_or_422(agent_point_event_in)
    agent_point_event = AgentPointEvent.model_validate(agent_point_event_in)
    session.add(agent_point_event)
    session.commit()
    session.refresh(agent_point_event)
    return agent_point_event


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
    agent_point_event = session.get(AgentPointEvent, agent_point_event_id)
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
    agent_point_event = session.get(AgentPointEvent, id)
    if not agent_point_event:
        raise HTTPException(status_code=404, detail="AgentPointEvent not found")
    ensure_event_schema_or_422(agent_point_event_in)
    update_dict = agent_point_event_in.model_dump(exclude_unset=True)
    agent_point_event.sqlmodel_update(update_dict)
    session.add(agent_point_event)
    session.commit()
    session.refresh(agent_point_event)
    return agent_point_event


@router.delete("/{agent_point_event_id}")
def delete_agent_point_event(
    session: SessionDep,
    _editor: AgentPointTableEditorUser,
    agent_point_event_id: int,
) -> Message:
    """
    Delete a agent_point_event.
    """
    agent_point_event = session.get(AgentPointEvent, agent_point_event_id)
    session.delete(agent_point_event)
    session.commit()
    return Message(message="AgentPointEvent deleted successfully")
