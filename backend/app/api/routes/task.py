from typing import Any

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    AgentPoint,
    Location,
    LocationEdge,
    LocationPublic,
    Message,
    Task,
    TaskMePublic,
    TaskPublic,
    TasksMePublic,
    TasksPublic,
)
from fastapi import APIRouter
from sqlalchemy.orm import load_only, selectinload
from sqlmodel import func, select

router = APIRouter(prefix="/tasks", tags=["tasks"])


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


from typing import Any, List, Optional

from geoalchemy2.functions import ST_Collect, ST_MakeLine
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import load_only, selectinload


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
        .options(
            selectinload(Task.agent_point),
        )
        .offset(skip)
        .limit(limit)
        .order_by(Task.start_time)
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
                # Use ST_Collect to combine all route parts
                collect_stmt = select(ST_Collect(route_parts))
                route = session.exec(collect_stmt).first()

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
