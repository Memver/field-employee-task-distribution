from sqlmodel import Session, col, func, select

from app.models import AgentPointEvent
from app.repositories.eager_loads import (
    agent_point_event_load_options,
    get_agent_point_event,
)


def get_by_id(*, session: Session, event_id: int) -> AgentPointEvent | None:
    return get_agent_point_event(session, event_id)


def get_by_id_for_agent_points(
    *, session: Session, event_id: int, agent_point_ids: list[int]
) -> AgentPointEvent | None:
    if not agent_point_ids:
        return None
    return session.exec(
        select(AgentPointEvent)
        .where(
            AgentPointEvent.id == event_id,
            col(AgentPointEvent.agent_point_id).in_(agent_point_ids),
        )
        .options(*agent_point_event_load_options())
    ).first()


def list_for_agent_points(
    *, session: Session, agent_point_ids: list[int], skip: int, limit: int
) -> list[AgentPointEvent]:
    if not agent_point_ids:
        return []
    return session.exec(
        select(AgentPointEvent)
        .where(col(AgentPointEvent.agent_point_id).in_(agent_point_ids))
        .options(*agent_point_event_load_options())
        .offset(skip)
        .limit(limit)
    ).all()


def count_for_agent_points(*, session: Session, agent_point_ids: list[int]) -> int:
    if not agent_point_ids:
        return 0
    return session.exec(
        select(func.count()).select_from(AgentPointEvent).where(
            col(AgentPointEvent.agent_point_id).in_(agent_point_ids)
        )
    ).one()


def save(*, session: Session, event: AgentPointEvent) -> AgentPointEvent:
    session.add(event)
    session.commit()
    loaded = get_agent_point_event(session, event.id)
    assert loaded is not None
    return loaded
