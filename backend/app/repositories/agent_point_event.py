from sqlmodel import Session, col, func, select

from app.models import AgentPointEvent


def get_by_id(*, session: Session, event_id: int) -> AgentPointEvent | None:
    return session.get(AgentPointEvent, event_id)


def get_by_id_for_agent_points(
    *, session: Session, event_id: int, agent_point_ids: list[int]
) -> AgentPointEvent | None:
    if not agent_point_ids:
        return None
    return session.exec(
        select(AgentPointEvent).where(
            AgentPointEvent.id == event_id,
            col(AgentPointEvent.agent_point_id).in_(agent_point_ids),
        )
    ).first()


def list_for_agent_points(
    *, session: Session, agent_point_ids: list[int], skip: int, limit: int
) -> list[AgentPointEvent]:
    if not agent_point_ids:
        return []
    return session.exec(
        select(AgentPointEvent)
        .where(col(AgentPointEvent.agent_point_id).in_(agent_point_ids))
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
    session.refresh(event)
    return event
