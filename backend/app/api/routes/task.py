from datetime import datetime, timezone
from typing import Any

import shapely
import shapely.wkb
from app.api.deps import CurrentUser, EmployeeManagerUser, FieldEmployeeUser, SessionDep
from app.core.roles import is_employee_manager_user, is_field_employee_user
from app.models import (
    AgentPoint,
    Employee,
    Location,
    LocationEdge,
    LocationPublic,
    Message,
    Task,
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
from fastapi import APIRouter, HTTPException
from shapely.ops import linemerge
from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload, load_only
from sqlmodel import func, select
from app.geocoding import get_lat_lon
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


def fill_location_edges_from_osm(session: SessionDep) -> tuple[int, int, int]:
    """
    Заполняет distance, time, route для рёбер с пустым или NULL route.
    Возвращает (число обновлённых, пропущено без координат, ошибка OSRM).
    """
    statement = select(LocationEdge).where(
        or_(
            LocationEdge.route.is_(None),
            func.coalesce(func.jsonb_array_length(LocationEdge.route), 0) == 0,
        )
    )
    edges = session.exec(statement).all()
    updated = 0
    skipped_no_coords = 0
    failed_osrm = 0

    for edge in edges:
        from_loc = session.get(Location, edge.from_location_id)
        to_loc = session.get(Location, edge.to_location_id)
        if (
            from_loc is None
            or to_loc is None
            or from_loc.lat is None
            or from_loc.lon is None
            or to_loc.lat is None
            or to_loc.lon is None
        ):
            skipped_no_coords += 1
            continue

        lon_a, lat_a = from_loc.lon, from_loc.lat
        lon_b, lat_b = to_loc.lon, to_loc.lat

        if from_loc.id == to_loc.id or (lat_a == lat_b and lon_a == lon_b):
            edge.distance = 0.0
            edge.time = 0
            edge.route = [[lon_a, lat_a], [lon_b, lat_b]]
            session.add(edge)
            updated += 1
            continue

        route_data = get_route_osm([(lat_a, lon_a), (lat_b, lon_b)])
        parsed = edge_fields_from_osm_response(route_data) if route_data else None
        if parsed is None:
            failed_osrm += 1
            continue

        distance_km, time_s, route_pts = parsed
        edge.distance = distance_km
        edge.time = time_s
        edge.route = route_pts
        session.add(edge)
        updated += 1

    if updated:
        session.commit()

    return updated, skipped_no_coords, failed_osrm


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
    # TODO: Удалить здесь геокодирование. Добавить геокодирование на этапе create, update location. Сразу будем и проверять адресс и сразу в бд записывать долготу широту.
    
    # TODO: для def distribute_ tasks (A.K.A solve()) нужны матрица расстояний, времени. для get_tasks_me нужен путь.
    # 1. развернуть локально osrm api Чтобы через docker поднимался для получения матрицы расстояний и времени и для получения пути на множество точек
    # Для def distribute
    # 2. Убрать получение путей из def distribute_tasks 
    # 3. получить матрицы расстояний и времени через api. В функцию получении матрицы расстояний добавить получение времени.
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
    location_ids = []

    # Add start location
    location_ids.append(current_employee.start_location_id)

    for task in tasks:
        tasks_me_public.append(TaskMePublic.model_validate(task))
        # Add task location
        if task.agent_point and task.agent_point.location:
            location_ids.append(task.agent_point.location.id)

    # Add start location again to complete the route (return to start)
    location_ids.append(current_employee.start_location_id)

    # Build route by finding paths between consecutive locations
    route = None

    if len(location_ids) > 1:
        # Create pairs of consecutive locations
        pairs = []
        for i in range(len(location_ids) - 1):
            from_id = location_ids[i]
            to_id = location_ids[i + 1]
            pairs.append((from_id, to_id))

        # Query edges for all pairs
        if pairs:
            # Build OR condition for all pairs
            conditions = []
            for from_id, to_id in pairs:
                conditions.append(
                    and_(
                        LocationEdge.from_location_id == from_id,
                        LocationEdge.to_location_id == to_id,
                    )
                )

            edge_statement = (
                select(LocationEdge)
                .where(or_(*conditions))
                .options(
                    load_only(
                        LocationEdge.route,
                        LocationEdge.from_location_id,
                        LocationEdge.to_location_id,
                    )
                )
            )

            edges = session.exec(edge_statement).all()

            # Create a dictionary for quick lookup
            edge_dict = {}
            for edge in edges:
                edge_dict[(edge.from_location_id, edge.to_location_id)] = edge.route

            # Collect routes in order
            route_parts = []
            for from_id, to_id in pairs:
                if (from_id, to_id) in edge_dict:
                    route_parts.append(edge_dict[(from_id, to_id)])

            # Combine all route parts into a single LineString if we have parts
            if route_parts:
                # Convert WKB elements to Shapely geometries
                geometries = []
                for wkb_element in route_parts:
                    # Assuming WKBElement contains WKB data
                    geom = shapely.wkb.loads(bytes(wkb_element.data))
                    geometries.append(geom)

                # Merge all LineStrings into one
                merged = linemerge(geometries)
                # Convert to WKT string instead of WKB binary
                route = shapely.wkt.dumps(merged)

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
