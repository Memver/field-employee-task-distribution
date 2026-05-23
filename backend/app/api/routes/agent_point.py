from typing import Any

from app.api.deps import (
    AgentPointReaderUser,
    AgentPointTableEditorUser,
    SessionDep,
    get_allowed_agent_point_ids_for_ap_manager,
)
from app.models import (
    AgentPoint,
    AgentPointCreate,
    AgentPointPublic,
    AgentPointsPublic,
    AgentPointUpdate,
    Message,
)
from app.repositories.eager_loads import agent_point_load_options, get_agent_point
from fastapi import APIRouter, HTTPException
from sqlmodel import col, func, select

router = APIRouter(prefix="/agent-points", tags=["agent-points"])


@router.post("/", response_model=AgentPointPublic)
def create_agent_point(
    *,
    session: SessionDep,
    _editor: AgentPointTableEditorUser,
    agent_point_in: AgentPointCreate,
) -> Any:
    """
    Create new agent_point.
    """
    agent_point = AgentPoint.model_validate(agent_point_in)
    session.add(agent_point)
    session.commit()
    agent_point = get_agent_point(session, agent_point.id)
    return agent_point


@router.get(
    "/",
    response_model=AgentPointsPublic,
)
def read_agent_points(
    session: SessionDep,
    reader: AgentPointReaderUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve agent_points (all for employee manager, scoped for agent point manager).
    """
    allowed_agent_point_ids = get_allowed_agent_point_ids_for_ap_manager(
        session=session, user_id=reader.id, role=reader.role
    )

    if allowed_agent_point_ids is not None:
        if not allowed_agent_point_ids:
            return AgentPointsPublic(data=[], count=0)
        count_statement = (
            select(func.count())
            .select_from(AgentPoint)
            .where(col(AgentPoint.id).in_(allowed_agent_point_ids))
        )
        count = session.exec(count_statement).one()
        statement = (
            select(AgentPoint)
            .where(col(AgentPoint.id).in_(allowed_agent_point_ids))
            .options(*agent_point_load_options())
            .offset(skip)
            .limit(limit)
        )
    else:
        count_statement = select(func.count()).select_from(AgentPoint)
        count = session.exec(count_statement).one()
        statement = (
            select(AgentPoint)
            .options(*agent_point_load_options())
            .offset(skip)
            .limit(limit)
        )

    agent_points = session.exec(statement).all()
    return AgentPointsPublic(data=agent_points, count=count)


@router.get("/{id}", response_model=AgentPointPublic)
def read_agent_point_by_id(
    id: int, session: SessionDep, reader: AgentPointReaderUser
) -> Any:
    """
    Get a specific agent_point by id.
    """
    allowed_agent_point_ids = get_allowed_agent_point_ids_for_ap_manager(
        session=session, user_id=reader.id, role=reader.role
    )
    if allowed_agent_point_ids is not None and id not in allowed_agent_point_ids:
        raise HTTPException(status_code=403, detail="Недостаточно прав для этой агентской точки")

    agent_point = get_agent_point(session, id)
    if not agent_point:
        raise HTTPException(status_code=404, detail="AgentPoint not found")
    return agent_point


@router.put("/{id}", response_model=AgentPointPublic)
def update_agent_point(
    *,
    session: SessionDep,
    editor: AgentPointTableEditorUser,
    id: int,
    agent_point_in: AgentPointUpdate,
) -> Any:
    """
    Update an agent_point.
    """
    allowed_agent_point_ids = get_allowed_agent_point_ids_for_ap_manager(
        session=session, user_id=editor.id, role=editor.role
    )
    if allowed_agent_point_ids is not None and id not in allowed_agent_point_ids:
        raise HTTPException(status_code=403, detail="Недостаточно прав для этой агентской точки")

    agent_point = session.get(AgentPoint, id)
    if not agent_point:
        raise HTTPException(status_code=404, detail="AgentPoint not found")
    update_dict = agent_point_in.model_dump(exclude_unset=True)
    agent_point.sqlmodel_update(update_dict)
    session.add(agent_point)
    session.commit()
    agent_point = get_agent_point(session, id)
    return agent_point


@router.delete("/{agent_point_id}")
def delete_agent_point(
    session: SessionDep, editor: AgentPointTableEditorUser, agent_point_id: int
) -> Message:
    """
    Delete a agent_point.
    """
    allowed_agent_point_ids = get_allowed_agent_point_ids_for_ap_manager(
        session=session, user_id=editor.id, role=editor.role
    )
    if (
        allowed_agent_point_ids is not None
        and agent_point_id not in allowed_agent_point_ids
    ):
        raise HTTPException(status_code=403, detail="Недостаточно прав для этой агентской точки")

    agent_point = session.get(AgentPoint, agent_point_id)
    if not agent_point:
        raise HTTPException(status_code=404, detail="AgentPoint not found")
    session.delete(agent_point)
    session.commit()
    return Message(message="AgentPoint deleted successfully")
