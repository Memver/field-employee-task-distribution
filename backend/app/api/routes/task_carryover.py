from datetime import datetime, timezone
from typing import Any

from app.api.deps import EmployeeManagerUser, SessionDep
from app.models import (
    AgentPoint,
    Message,
    TaskCarryover,
    TaskCarryoverCreate,
    TaskCarryoverPublic,
    TaskCarryoversPublic,
    TaskCarryoverUpdate,
    TaskType,
)
from app.repositories import task_carryover as task_carryover_repository
from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlmodel import func, select

router = APIRouter(prefix="/task-carryovers", tags=["task-carryovers"])


def _get_with_relations(*, session: SessionDep, task_carryover_id: int) -> TaskCarryover | None:
    statement = (
        select(TaskCarryover)
        .options(
            joinedload(TaskCarryover.agent_point).joinedload(AgentPoint.location),
            joinedload(TaskCarryover.task_type).joinedload(TaskType.min_grade),
            joinedload(TaskCarryover.task_type).joinedload(TaskType.priority),
        )
        .where(TaskCarryover.id == task_carryover_id)
    )
    return session.exec(statement).first()


@router.post("/", response_model=TaskCarryoverPublic)
def create_task_carryover(
    *,
    session: SessionDep,
    _em: EmployeeManagerUser,
    task_carryover_in: TaskCarryoverCreate,
) -> Any:
    if not session.get(AgentPoint, task_carryover_in.agent_point_id):
        raise HTTPException(status_code=404, detail="AgentPoint not found")
    if not session.get(TaskType, task_carryover_in.task_type_id):
        raise HTTPException(status_code=404, detail="TaskType not found")

    task_carryover = TaskCarryover.model_validate(task_carryover_in)
    now_utc = datetime.now(timezone.utc)
    task_carryover.created_at = now_utc
    task_carryover.updated_at = now_utc
    try:
        created = task_carryover_repository.create(session=session, item=task_carryover)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=409,
            detail=(
                "TaskCarryover with same agent_point_id, task_type_id and planned_for_date "
                "already exists"
            ),
        ) from exc
    return _get_with_relations(session=session, task_carryover_id=created.id)


@router.get("/", response_model=TaskCarryoversPublic)
def read_task_carryovers(
    session: SessionDep, _em: EmployeeManagerUser, skip: int = 0, limit: int = 100
) -> Any:
    count_statement = select(func.count()).select_from(TaskCarryover)
    count = session.exec(count_statement).one()
    statement = (
        select(TaskCarryover)
        .options(
            joinedload(TaskCarryover.agent_point).joinedload(AgentPoint.location),
            joinedload(TaskCarryover.task_type).joinedload(TaskType.min_grade),
            joinedload(TaskCarryover.task_type).joinedload(TaskType.priority),
        )
        .offset(skip)
        .limit(limit)
    )
    task_carryovers = session.exec(statement).all()
    return TaskCarryoversPublic(data=task_carryovers, count=count)


@router.get("/{task_carryover_id}", response_model=TaskCarryoverPublic)
def read_task_carryover_by_id(
    task_carryover_id: int, session: SessionDep, _em: EmployeeManagerUser
) -> Any:
    task_carryover = _get_with_relations(
        session=session, task_carryover_id=task_carryover_id
    )
    if not task_carryover:
        raise HTTPException(status_code=404, detail="TaskCarryover not found")
    return task_carryover


@router.put("/{task_carryover_id}", response_model=TaskCarryoverPublic)
def update_task_carryover(
    *,
    session: SessionDep,
    _em: EmployeeManagerUser,
    task_carryover_id: int,
    task_carryover_in: TaskCarryoverUpdate,
) -> Any:
    task_carryover = task_carryover_repository.get_by_id(
        session=session, task_carryover_id=task_carryover_id
    )
    if not task_carryover:
        raise HTTPException(status_code=404, detail="TaskCarryover not found")
    if not session.get(AgentPoint, task_carryover_in.agent_point_id):
        raise HTTPException(status_code=404, detail="AgentPoint not found")
    if not session.get(TaskType, task_carryover_in.task_type_id):
        raise HTTPException(status_code=404, detail="TaskType not found")

    update_dict = task_carryover_in.model_dump(exclude_unset=True)
    update_dict["updated_at"] = datetime.now(timezone.utc)
    task_carryover.sqlmodel_update(update_dict)
    try:
        updated = task_carryover_repository.update(session=session, item=task_carryover)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=409,
            detail=(
                "TaskCarryover with same agent_point_id, task_type_id and planned_for_date "
                "already exists"
            ),
        ) from exc
    return _get_with_relations(session=session, task_carryover_id=updated.id)


@router.delete("/{task_carryover_id}")
def delete_task_carryover(
    session: SessionDep, _em: EmployeeManagerUser, task_carryover_id: int
) -> Message:
    task_carryover = task_carryover_repository.get_by_id(
        session=session, task_carryover_id=task_carryover_id
    )
    if not task_carryover:
        raise HTTPException(status_code=404, detail="TaskCarryover not found")
    task_carryover_repository.delete(session=session, item=task_carryover)
    return Message(message="TaskCarryover deleted successfully")
