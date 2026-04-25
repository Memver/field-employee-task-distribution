from datetime import datetime, timezone
from typing import Any

from app.api.deps import (
    AgentPointManagerUser,
    CurrentUser,
    EmployeeManagerUser,
    FieldEmployeeUser,
    SessionDep,
)
from app.core.roles import is_employee_manager_user, is_field_employee_user
from app.models import (
    AgentPointEvent,
    AgentPoint,
    Employee,
    Location,
    LocationPublic,
    Message,
    TaskCompleteUpdate,
    TaskSkipUpdate,
    Task,
    TaskAgentPointManagerConfirmUpdate,
    TaskCreate,
    TaskMePublic,
    TaskPublic,
    TaskSelfUpdate,
    TaskStatus,
    TaskType,
    TasksMePublic,
    TasksPublic,
    TaskUpdate,
)
from app.distribute import solve as distribute_solve
from app.services.agent_point_events import build_agent_point_metrics_snapshots
from fastapi import APIRouter, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from sqlmodel import func, select
from app.path import edge_fields_from_osm_response, get_route_osm
from ...distanse_matrix import get_distance_and_time_matrix

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_locations_without_coordinates(session: SessionDep) -> list[Location]:
    statement = select(Location).where(or_(Location.lat.is_(None), Location.lon.is_(None)))
    return session.exec(statement).all()


def update_locations_with_coordinates(
    session: SessionDep,
    locations: list[Location],
    coordinates: list[tuple[float | None, float | None]],
) -> int:
    updated_count = 0

    for location, (lat, lon) in zip(locations, coordinates):
        if lat is None or lon is None:
            continue

        location.lat = lat
        location.lon = lon
        session.add(location)
        updated_count += 1

    if updated_count:
        session.commit()

    return updated_count


def get_all_locations(session: SessionDep) -> list[Location]:
    statement = select(Location)
    return session.exec(statement).all()


@router.post("/", response_model=TaskPublic)
def create_task(
    *, session: SessionDep, _em: EmployeeManagerUser, task_in: TaskCreate
) -> Any:
    """
    Create new task.
    """
    task = Task.model_validate(task_in)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.post("/distribute")
def distribute_tasks(*, session: SessionDep, _em: EmployeeManagerUser) -> Message:
    # для def distribute_ tasks (A.K.A solve()) нужны матрица расстояний, времени. для get_tasks_me нужен путь.
    # 1. развернуть локально osrm api Чтобы через docker поднимался для получения матрицы расстояний и времени и для получения пути на множество точек
    # Для def distribute
    # 2. получить матрицы расстояний и времени через api. В функцию получении матрицы расстояний добавить получение времени.
    # Для def get tasks_me
    # 2. получить путь через api

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
        select(TaskType).options(
            joinedload(TaskType.min_grade),
            joinedload(TaskType.priority),
        )
    ).all()

    locations = get_all_locations(session)
    distance_matrix, time_matrix = get_distance_and_time_matrix(locations)

    assigned_status = session.exec(
        select(TaskStatus).where(TaskStatus.name == "ASSIGNED")
    ).first()
    if assigned_status is None:
        return Message(
            message=(
                "Task status 'ASSIGNED' not found. "
                "Distribution cancelled."
            )
        )

    old_assigned_tasks = session.exec(
        select(Task).where(Task.task_status_id == assigned_status.id)
    ).all()

    # Динамический приоритет для переносимых задач:
    # если точка уже была в ASSIGNED, но не закрыта, увеличиваем ее penalty на drop.
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

    planned_tasks = distribute_solve(
        employees=employees,
        agent_points=agent_points,
        task_types=task_types,
        locations=locations,
        time_matrix=time_matrix,
        horizon_days=3,
        carryover_days_by_agent_point=carryover_days_by_agent_point,
        snapshots_by_agent_point=snapshots_by_agent_point,
    )

    # Перераспределение всегда пересоздает активные задачи статуса ASSIGNED.
    for old_task in old_assigned_tasks:
        session.delete(old_task)

    created_count = 0
    for planned_task in planned_tasks:
        task = Task(
            employee_id=planned_task.employee_id,
            agent_point_id=planned_task.agent_point_id,
            task_type_id=planned_task.task_type_id,
            task_status_id=assigned_status.id,
            start_time=planned_task.start_time,
            finish_time=planned_task.finish_time,
            comment=planned_task.comment,
        )
        session.add(task)
        created_count += 1

    session.commit()

    return Message(
        message=(
            f"Distribution completed. "
            f"Matrices prepared for solve: {len(locations)}x{len(locations)}. "
            f"Loaded employees={len(employees)}, "
            f"agent_points={len(agent_points)}, "
            f"task_types={len(task_types)}. "
            f"Removed old assigned={len(old_assigned_tasks)}, "
            f"created assigned={created_count}."
        )
    )


@router.get(
    "/",
    response_model=TasksPublic,
)
def read_tasks(
    session: SessionDep, _em: EmployeeManagerUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve tasks.
    """

    count_statement = select(func.count()).select_from(Task)
    count = session.exec(count_statement).one()

    statement = select(Task).offset(skip).limit(limit)
    tasks = session.exec(statement).all()

    return TasksPublic(data=tasks, count=count)


@router.get("/me", response_model=TasksMePublic)
def read_tasks_me(
    session: SessionDep,
    field_user: FieldEmployeeUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve my tasks with route path from start location through all tasks and back.
    """
    current_employee = field_user.employee

    # Get start location
    start_location = session.get(Location, current_employee.start_location_id)

    # Query tasks for current employee with pagination
    statement = (
        select(Task)
        .where(Task.employee_id == current_employee.id)
        .options(joinedload(Task.agent_point).selectinload(AgentPoint.location))
        .order_by(Task.start_time)
        .offset(skip)
        .limit(limit)
    )
    #     statement = (
    #     select(Task)
    #     .where(Task.employee_id == current_employee.id)
    #     .offset(skip)
    #     .limit(limit)
    #     .options(
    #         selectinload(Task.agent_point).selectinload(AgentPoint.location),
    #     )
    #     .order_by(Task.start_time)
    # )
    tasks = session.exec(statement).all()

    # Prepare task list for response
    tasks_me_public = []
    points: list[tuple[float, float]] = []
    if start_location and start_location.lat is not None and start_location.lon is not None:
        # path.py expects points as (lat, lon)
        points.append((start_location.lat, start_location.lon))

    for task in tasks:
        tasks_me_public.append(TaskMePublic.model_validate(task))
        if (
            task.agent_point
            and task.agent_point.location
            and task.agent_point.location.lat is not None
            and task.agent_point.location.lon is not None
        ):
            points.append((task.agent_point.location.lat, task.agent_point.location.lon))

    if start_location and start_location.lat is not None and start_location.lon is not None:
        points.append((start_location.lat, start_location.lon))

    route: list[list[float]] | None = None
    if len(points) >= 2:
        route_data = get_route_osm(points)
        parsed_route = edge_fields_from_osm_response(route_data) if route_data else None
        if parsed_route is not None:
            _distance_km, _time_seconds, route_points = parsed_route
            route = route_points

    return TasksMePublic(
        tasks=tasks_me_public,
        route=route,
        start_location=LocationPublic.model_validate(start_location),
    )


@router.patch("/{task_id}/self", response_model=TaskPublic)
def update_my_task_status(
    *,
    session: SessionDep,
    field_user: FieldEmployeeUser,
    task_id: int,
    body: TaskSelfUpdate,
) -> Any:
    """
    Выездной сотрудник: смена статуса и комментария только по своей задаче.
    """
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.employee_id != field_user.employee.id:
        raise HTTPException(
            status_code=403,
            detail="Можно изменять только свои задачи",
        )
    task.task_status_id = body.task_status_id
    if body.comment is not None:
        task.comment = body.comment
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.patch("/{task_id}/complete", response_model=TaskPublic)
def complete_my_task(
    *,
    session: SessionDep,
    field_user: FieldEmployeeUser,
    task_id: int,
    body: TaskCompleteUpdate,
) -> Any:
    """
    Выездной сотрудник: отметить свою задачу как выполненную.
    """
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.employee_id != field_user.employee.id:
        raise HTTPException(
            status_code=403,
            detail="Можно изменять только свои задачи",
        )

    completed_status = session.exec(
        select(TaskStatus).where(TaskStatus.name == "COMPLETED")
    ).first()
    if completed_status is None:
        raise HTTPException(
            status_code=500,
            detail="Task status 'COMPLETED' not found",
        )

    task.task_status_id = completed_status.id
    if body.comment is not None:
        task.comment = body.comment
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.patch("/{task_id}/skip", response_model=TaskPublic)
def skip_my_task(
    *,
    session: SessionDep,
    field_user: FieldEmployeeUser,
    task_id: int,
    body: TaskSkipUpdate,
) -> Any:
    """
    Выездной сотрудник: пропустить свою задачу с указанием причины.
    """
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.employee_id != field_user.employee.id:
        raise HTTPException(
            status_code=403,
            detail="Можно изменять только свои задачи",
        )

    skipped_status = session.exec(
        select(TaskStatus).where(TaskStatus.name == "SKIPPED")
    ).first()
    if skipped_status is None:
        raise HTTPException(
            status_code=500,
            detail="Task status 'SKIPPED' not found",
        )

    task.task_status_id = skipped_status.id
    task.comment = body.comment
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.patch("/{task_id}/complete-by-agent-point-manager", response_model=TaskPublic)
def complete_task_by_agent_point_manager(
    *,
    session: SessionDep,
    apm: AgentPointManagerUser,
    task_id: int,
    body: TaskAgentPointManagerConfirmUpdate,
) -> Any:
    """
    Менеджер агентской точки: подтвердить или отклонить статус задачи.
    """
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.ap_manager_confirmed = body.confirmed
    task.ap_manager_comment = body.comment
    task.ap_manager_user_id = apm.id

    if body.confirmed:
        task_type = session.get(TaskType, task.task_type_id)
        if task_type is not None and task_type.name == "CARDS_DELIVERY":
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


@router.get("/{task_id}", response_model=TaskPublic)
def read_task_by_id(
    task_id: int, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific task by id.
    """
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if is_employee_manager_user(current_user.role):
        return task
    if (
        is_field_employee_user(current_user.role)
        and current_user.employee is not None
        and task.employee_id == current_user.employee.id
    ):
        return task
    raise HTTPException(
        status_code=403,
        detail="Недостаточно прав для просмотра этой задачи",
    )


@router.put("/{id}", response_model=TaskPublic)
def update_task(
    *,
    session: SessionDep,
    _em: EmployeeManagerUser,
    id: int,
    task_in: TaskUpdate,
) -> Any:
    """
    Update an task.
    """
    task = session.get(Task, id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    update_dict = task_in.model_dump(exclude_unset=True)
    task.sqlmodel_update(update_dict)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.delete("/{task_id}")
def delete_task(
    session: SessionDep, _em: EmployeeManagerUser, task_id: int
) -> Message:
    """
    Delete a task.
    """
    task = session.get(Task, task_id)
    # statement = delete(Item).where(col(Item.owner_id) == task_id)
    # session.exec(statement)
    session.delete(task)
    session.commit()
    return Message(message="Task deleted successfully")
