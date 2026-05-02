from fastapi import HTTPException
from sqlmodel import Session

from app.models import AgentPointEvent, AgentPointEventCreate, AgentPointEventUpdate
from app.repositories import agent_point_event as event_repository
from app.services.agent_point_event_schema import validate_agent_point_event_payload


def validate_or_422(*, payload: AgentPointEventCreate | AgentPointEventUpdate) -> None:
    try:
        validate_agent_point_event_payload(
            event_type=payload.event_type,
            metric_name=payload.metric_name,
            metric_delta=payload.metric_delta,
            metric_value_num=payload.metric_value_num,
            metric_value_bool=payload.metric_value_bool,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def create_event(*, session: Session, payload: AgentPointEventCreate) -> AgentPointEvent:
    validate_or_422(payload=payload)
    event = AgentPointEvent.model_validate(payload)
    return event_repository.save(session=session, event=event)


def update_event(
    *,
    session: Session,
    event: AgentPointEvent,
    payload: AgentPointEventUpdate,
) -> AgentPointEvent:
    validate_or_422(payload=payload)
    event.sqlmodel_update(payload.model_dump(exclude_unset=True))
    return event_repository.save(session=session, event=event)
