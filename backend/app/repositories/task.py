from sqlmodel import Session, select

from app.models import Task


def get_by_id(*, session: Session, task_id: int) -> Task | None:
    return session.get(Task, task_id)


def get_by_status_id(*, session: Session, task_status_id: int) -> list[Task]:
    return session.exec(select(Task).where(Task.task_status_id == task_status_id)).all()


def replace_assigned_tasks(
    *,
    session: Session,
    old_assigned_tasks: list[Task],
    new_tasks: list[Task],
) -> None:
    for old_task in old_assigned_tasks:
        session.delete(old_task)
    for task in new_tasks:
        session.add(task)
    session.commit()
