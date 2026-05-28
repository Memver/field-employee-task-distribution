from datetime import date

from sqlmodel import Session, and_, or_, select

from app.models import TaskCarryover


def get_due_backlog(*, session: Session, today: date) -> list[TaskCarryover]:
    statement = select(TaskCarryover).where(TaskCarryover.planned_for_date <= today)
    return session.exec(statement).all()


def get_by_keys(
    *,
    session: Session,
    key_pairs: set[tuple[int, int]],
    planned_for_dates: set[date],
) -> list[TaskCarryover]:
    if not key_pairs or not planned_for_dates:
        return []
    predicates = [
        and_(
            TaskCarryover.agent_point_id == agent_point_id,
            TaskCarryover.task_type_id == task_type_id,
        )
        for agent_point_id, task_type_id in key_pairs
    ]
    statement = select(TaskCarryover).where(
        or_(*predicates),
        TaskCarryover.planned_for_date.in_(planned_for_dates),
    )
    return session.exec(statement).all()


def remove_by_ids(*, session: Session, item_ids: set[int]) -> int:
    if not item_ids:
        return 0
    items = session.exec(
        select(TaskCarryover).where(TaskCarryover.id.in_(item_ids))
    ).all()
    for item in items:
        session.delete(item)
    return len(items)


def get_by_id(*, session: Session, task_carryover_id: int) -> TaskCarryover | None:
    return session.get(TaskCarryover, task_carryover_id)


def list_paginated(*, session: Session, skip: int = 0, limit: int = 100) -> list[TaskCarryover]:
    statement = select(TaskCarryover).offset(skip).limit(limit)
    return session.exec(statement).all()


def count(*, session: Session) -> int:
    statement = select(TaskCarryover)
    return len(session.exec(statement).all())


def create(*, session: Session, item: TaskCarryover) -> TaskCarryover:
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def update(*, session: Session, item: TaskCarryover) -> TaskCarryover:
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def delete(*, session: Session, item: TaskCarryover) -> None:
    session.delete(item)
    session.commit()
