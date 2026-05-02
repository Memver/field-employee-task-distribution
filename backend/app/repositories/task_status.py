from sqlmodel import Session, select

from app.models import TaskStatus


def get_by_name(*, session: Session, name: str) -> TaskStatus | None:
    return session.exec(select(TaskStatus).where(TaskStatus.name == name)).first()


def ensure_exists(*, session: Session, name: str) -> TaskStatus:
    status = get_by_name(session=session, name=name)
    if status is not None:
        return status
    status = TaskStatus(name=name)
    session.add(status)
    session.commit()
    session.refresh(status)
    return status
