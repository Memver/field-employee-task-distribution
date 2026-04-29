from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select

from app.core.constants import TaskStatusName, TaskTypeName
from app.distribute import solve as distribute_solve
from app.distanse_matrix import get_distance_and_time_matrix
from app.models import (
    AgentPoint,
    AgentPointEvent,
    DistributionAssignmentPublic,
    DistributionReportPublic,
    DistributionUnplacedPublic,
    Employee,
    Location,
    LocationPublic,
    Message,
    Task,
    TaskMePublic,
    TaskStatus,
    TaskType,
    TasksMePublic,
)
from app.repositories import task as task_repository
from app.repositories import task_status as task_status_repository
from app.services.agent_point_events import build_agent_point_metrics_snapshots
from app.services.routing_gateway import build_route

def distribute_tasks(*, session: Session) -> DistributionReportPublic:
    employees = session.exec(
        select(Employee).options(
            joinedload(Employee.user),
            joinedload(Employee.grade),
            joinedload(Employee.start_location),
        )
    ).all()
    agent_points = session.exec(
        select(AgentPoint).options(joinedload(AgentPoint.location))
    ).all()
    snapshots_by_agent_point = build_agent_point_metrics_snapshots(
        session=session,
        agent_point_ids=[agent_point.id for agent_point in agent_points],
        report_time=datetime.now(timezone.utc),
    )
    task_types = session.exec(
        select(TaskType).options(joinedload(TaskType.min_grade), joinedload(TaskType.priority))
    ).all()
    locations = session.exec(select(Location)).all()
    _distance_matrix, time_matrix = get_distance_and_time_matrix(locations)

    assigned_status = task_status_repository.get_by_name(
        session=session, name=TaskStatusName.ASSIGNED.value
    )
    if assigned_status is None:
        return DistributionReportPublic(
            message="Статус задачи 'ASSIGNED' не найден. Распределение отменено.",
            assignments=[],
            unplaced=[],
        )

    old_assigned_tasks = task_repository.get_by_status_id(
        session=session, task_status_id=assigned_status.id
    )

    today_utc = datetime.now(timezone.utc).date()
    carryover_days_by_agent_point: dict[int, int] = {}
    for old_task in old_assigned_tasks:
        if old_task.start_time is None:
            continue
        task_date = old_task.start_time
        if task_date.tzinfo is None:
            task_date = task_date.replace(tzinfo=timezone.utc)
        age_days = max((today_utc - task_date.date()).days, 0)
        prev = carryover_days_by_agent_point.get(old_task.agent_point_id, 0)
        carryover_days_by_agent_point[old_task.agent_point_id] = max(prev, age_days + 1)

    report = distribute_solve(
        employees=employees,
        agent_points=agent_points,
        task_types=task_types,
        locations=locations,
        time_matrix=time_matrix,
        horizon_days=1,
        carryover_days_by_agent_point=carryover_days_by_agent_point,
        snapshots_by_agent_point=snapshots_by_agent_point,
    )
    new_tasks = [
        Task(
            employee_id=planned_task.employee_id,
            agent_point_id=planned_task.agent_point_id,
            task_type_id=planned_task.task_type_id,
            task_status_id=assigned_status.id,
            start_time=planned_task.start_time,
            finish_time=planned_task.finish_time,
            comment=planned_task.comment,
        )
        for planned_task in report.planned_tasks
    ]
    task_repository.replace_assigned_tasks(
        session=session, old_assigned_tasks=old_assigned_tasks, new_tasks=new_tasks
    )
    message = (
        f"Распределение завершено. Матрицы подготовлены для расчета: {len(locations)}x{len(locations)}. "
        f"Загружено сотрудников={len(employees)}, агентских точек={len(agent_points)}, типов задач={len(task_types)}. "
        f"Удалено старых назначенных={len(old_assigned_tasks)}, создано назначенных={len(new_tasks)}, "
        f"неразмещенных={len(report.unplaced)}."
    )
    return DistributionReportPublic(
        message=message,
        assignments=[
            DistributionAssignmentPublic(
                employee_id=assignment.employee_id,
                employee_full_name=assignment.employee_full_name,
                agent_point_id=assignment.agent_point_id,
                agent_point_address=assignment.agent_point_address,
                task_type_id=assignment.task_type_id,
                task_type_name=assignment.task_type_name,
                day_index=assignment.day_index,
                start_time=assignment.start_time,
                finish_time=assignment.finish_time,
                reason=assignment.reason,
            )
            for assignment in report.assignments
        ],
        unplaced=[
            DistributionUnplacedPublic(
                agent_point_id=item.agent_point_id,
                agent_point_address=item.agent_point_address,
                task_type_id=item.task_type_id,
                task_type_name=item.task_type_name,
                reason=item.reason,
            )
            for item in report.unplaced
        ],
    )


def read_tasks_me(*, session: Session, employee_id: int, start_location_id: int, skip: int, limit: int) -> TasksMePublic:
    start_location = session.get(Location, start_location_id)
    tasks = session.exec(
        select(Task)
        .where(Task.employee_id == employee_id)
        .options(joinedload(Task.agent_point).selectinload(AgentPoint.location))
        .order_by(Task.start_time)
        .offset(skip)
        .limit(limit)
    ).all()
    tasks_public: list[TaskMePublic] = [TaskMePublic.model_validate(task) for task in tasks]

    points: list[tuple[float, float]] = []
    if start_location and start_location.lat is not None and start_location.lon is not None:
        points.append((start_location.lat, start_location.lon))
    for task in tasks:
        if (
            task.agent_point
            and task.agent_point.location
            and task.agent_point.location.lat is not None
            and task.agent_point.location.lon is not None
        ):
            points.append((task.agent_point.location.lat, task.agent_point.location.lon))
    if start_location and start_location.lat is not None and start_location.lon is not None:
        points.append((start_location.lat, start_location.lon))

    route = build_route(points)
    return TasksMePublic(
        tasks=tasks_public,
        route=route,
        start_location=LocationPublic.model_validate(start_location),
    )


def mark_task_completed(*, session: Session, task: Task, comment: str | None) -> Task:
    completed_status = _status_or_500(session=session, name=TaskStatusName.COMPLETED.value)
    task.task_status_id = completed_status.id
    if comment is not None:
        task.comment = comment
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def mark_task_skipped(*, session: Session, task: Task, comment: str) -> Task:
    skipped_status = _status_or_500(session=session, name=TaskStatusName.SKIPPED.value)
    task.task_status_id = skipped_status.id
    task.comment = comment
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def confirm_task_by_ap_manager(
    *,
    session: Session,
    task: Task,
    ap_manager_id: int,
    confirmed: bool,
    comment: str | None,
) -> Task:
    task.ap_manager_confirmed = confirmed
    task.ap_manager_comment = comment
    task.ap_manager_user_id = ap_manager_id
    if confirmed:
        task_type = session.get(TaskType, task.task_type_id)
        if task_type is not None and task_type.name == TaskTypeName.CARDS_DELIVERY.value:
            session.add(
                AgentPointEvent(
                    agent_point_id=task.agent_point_id,
                    event_time=task.finish_time,
                    event_type="cards_delivery_status_changed",
                    metric_name="is_cards_delivered",
                    metric_value_bool=True,
                )
            )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def _status_or_500(*, session: Session, name: str) -> TaskStatus:
    status = task_status_repository.get_by_name(session=session, name=name)
    if status is None:
        raise HTTPException(status_code=500, detail=f"Task status '{name}' not found")
    return status
