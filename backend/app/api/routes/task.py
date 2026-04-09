from typing import Any

import shapely
import shapely.wkb
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    AgentPoint,
    Location,
    LocationEdge,
    LocationPublic,
    Message,
    Task,
    TaskCreate,
    TaskMePublic,
    TaskPublic,
    TasksMePublic,
    TasksPublic,
    TaskUpdate,
)
from fastapi import APIRouter, HTTPException
from shapely.ops import linemerge
from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload, load_only
from sqlmodel import func, select
from app.geocoding import get_lat_lon

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


@router.post("/", response_model=TaskPublic)
def create_task(*, session: SessionDep, task_in: TaskCreate) -> Any:
    """
    Create new task.
    """
    task = Task.model_validate(task_in)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.post("/distribute")
def distribute_tasks(*, session: SessionDep) -> Message:
    locations_without_coordinates = get_locations_without_coordinates(session)

    if locations_without_coordinates:
        addresses = [location.address for location in locations_without_coordinates]
        coordinates = get_lat_lon(addresses)
        updated_count = update_locations_with_coordinates(
            session, locations_without_coordinates, coordinates
        )

        remaining_without_coordinates = get_locations_without_coordinates(session)
        if remaining_without_coordinates:
            unresolved_addresses = ", ".join(
                location.address for location in remaining_without_coordinates[:3]
            )
            if len(remaining_without_coordinates) > 3:
                unresolved_addresses += ", ..."

            return Message(
                message=(
                    f"Geocoding partially completed: updated {updated_count} locations. "
                    f"Still missing coordinates for {len(remaining_without_coordinates)} "
                    f"locations: {unresolved_addresses}"
                )
            )

        return Message(
            message=f"Coordinates updated for {updated_count} locations. "
            "Task distribution is not implemented yet."
        )
    # distance_matrix = api.get_distance_matrix()

    # solve(distance_matrix, num_vehicles, starts, ends, max_visits_per_vehicle)

    return Message(message="All locations already have coordinates.")


@router.get(
    "/",
    response_model=TasksPublic,
)
def read_tasks(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
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
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve my tasks with route path from start location through all tasks and back.
    """
    # Get current employee
    current_employee = current_user.employee

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

    print(tasks)

    # Prepare task list for response
    tasks_me_public = []
    location_ids = []

    # Add start location
    location_ids.append(current_employee.start_location_id)

    print(location_ids)

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

    print(tasks)
    print(route)
    print(start_location)

    return TasksMePublic(
        tasks=tasks_me_public,
        route=route,
        start_location=LocationPublic.model_validate(start_location),
    )


@router.get("/{task_id}", response_model=TaskPublic)
def read_task_by_id(task_id: int, session: SessionDep) -> Any:
    """
    Get a specific task by id.
    """
    task = session.get(Task, task_id)
    return task


@router.put("/{id}", response_model=TaskPublic)
def update_task(
    *,
    session: SessionDep,
    current_user: CurrentUser,
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
def delete_task(session: SessionDep, task_id: int) -> Message:
    """
    Delete a task.
    """
    task = session.get(Task, task_id)
    # statement = delete(Item).where(col(Item.owner_id) == task_id)
    # session.exec(statement)
    session.delete(task)
    session.commit()
    return Message(message="Task deleted successfully")
