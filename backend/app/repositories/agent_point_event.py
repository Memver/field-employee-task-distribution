from sqlmodel import Session

from app.models import AgentPointEvent


def get_by_id(*, session: Session, event_id: int) -> AgentPointEvent | None:
    return session.get(AgentPointEvent, event_id)


def save(*, session: Session, event: AgentPointEvent) -> AgentPointEvent:
    session.add(event)
    session.commit()
    session.refresh(event)
    return event
