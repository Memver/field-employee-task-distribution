from sqlalchemy.orm import joinedload
from sqlmodel import Session

from app.models import (
    AgentPoint,
    AgentPointEvent,
    Employee,
    Task,
    TaskType,
    User,
)


def employee_load_options():
    return (
        joinedload(Employee.user),
        joinedload(Employee.grade),
        joinedload(Employee.start_location),
    )


def task_type_load_options():
    return (
        joinedload(TaskType.min_grade),
        joinedload(TaskType.priority),
    )


def agent_point_load_options():
    return (joinedload(AgentPoint.location),)


def agent_point_event_load_options():
    return (
        joinedload(AgentPointEvent.agent_point).joinedload(AgentPoint.location),
    )


def task_load_options():
    return (
        joinedload(Task.employee).joinedload(Employee.user),
        joinedload(Task.employee).joinedload(Employee.grade),
        joinedload(Task.employee).joinedload(Employee.start_location),
        joinedload(Task.task_type).joinedload(TaskType.min_grade),
        joinedload(Task.task_type).joinedload(TaskType.priority),
        joinedload(Task.agent_point).joinedload(AgentPoint.location),
        joinedload(Task.task_status),
    )


def get_employee(session: Session, employee_id: int) -> Employee | None:
    return session.get(Employee, employee_id, options=employee_load_options())


def get_task_type(session: Session, task_type_id: int) -> TaskType | None:
    return session.get(TaskType, task_type_id, options=task_type_load_options())


def get_agent_point(session: Session, agent_point_id: int) -> AgentPoint | None:
    return session.get(AgentPoint, agent_point_id, options=agent_point_load_options())


def get_agent_point_event(session: Session, event_id: int) -> AgentPointEvent | None:
    return session.get(
        AgentPointEvent, event_id, options=agent_point_event_load_options()
    )


def get_task(session: Session, task_id: int) -> Task | None:
    return session.get(Task, task_id, options=task_load_options())
