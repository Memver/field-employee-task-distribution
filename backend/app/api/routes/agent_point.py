from typing import Any

from app.api.deps import AgentPointReaderUser, AgentPointTableEditorUser, SessionDep
from app.models import (
    AgentPoint,
    AgentPointCreate,
    AgentPointPublic,
    AgentPointsPublic,
    AgentPointUpdate,
    Message,
)
from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

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
    session.refresh(agent_point)
    return agent_point


@router.get(
    "/",
    response_model=AgentPointsPublic,
)
def read_agent_points(
    session: SessionDep, _reader: AgentPointReaderUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve agent_points.
    """

    count_statement = select(func.count()).select_from(AgentPoint)
    count = session.exec(count_statement).one()

    statement = select(AgentPoint).offset(skip).limit(limit)
    agent_points = session.exec(statement).all()

    return AgentPointsPublic(data=agent_points, count=count)


@router.get("/{id}", response_model=AgentPointPublic)
def read_agent_point_by_id(
    id: int, session: SessionDep, _reader: AgentPointReaderUser
) -> Any:
    """
    Get a specific agent_point by id.
    """
    agent_point = session.get(AgentPoint, id)
    return agent_point


@router.put("/{id}", response_model=AgentPointPublic)
def update_agent_point(
    *,
    session: SessionDep,
    _editor: AgentPointTableEditorUser,
    id: int,
    agent_point_in: AgentPointUpdate,
) -> Any:
    """
    Update an agent_point.
    """
    agent_point = session.get(AgentPoint, id)
    if not agent_point:
        raise HTTPException(status_code=404, detail="AgentPoint not found")
    update_dict = agent_point_in.model_dump(exclude_unset=True)
    agent_point.sqlmodel_update(update_dict)
    session.add(agent_point)
    session.commit()
    session.refresh(agent_point)
    return agent_point


@router.delete("/{agent_point_id}")
def delete_agent_point(
    session: SessionDep, _editor: AgentPointTableEditorUser, agent_point_id: int
) -> Message:
    """
    Delete a agent_point.
    """
    agent_point = session.get(AgentPoint, agent_point_id)
    session.delete(agent_point)
    session.commit()
    return Message(message="AgentPoint deleted successfully")
