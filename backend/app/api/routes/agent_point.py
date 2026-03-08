from typing import Any

from app.api.deps import SessionDep
from app.models import AgentPoint, AgentPointPublic, AgentPointsPublic, Message
from fastapi import APIRouter
from sqlmodel import func, select

router = APIRouter(prefix="/agent-points", tags=["agent-points"])


@router.get(
    "/",
    response_model=AgentPointsPublic,
)
def read_agent_points(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve agent_points.
    """

    count_statement = select(func.count()).select_from(AgentPoint)
    count = session.exec(count_statement).one()

    statement = select(AgentPoint).offset(skip).limit(limit)
    agent_points = session.exec(statement).all()

    return AgentPointsPublic(data=agent_points, count=count)


@router.get("/{agent_point_id}", response_model=AgentPointPublic)
def read_agent_point_by_id(agent_point_id: int, session: SessionDep) -> Any:
    """
    Get a specific agent_point by id.
    """
    agent_point = session.get(AgentPoint, agent_point_id)
    return agent_point


@router.delete("/{agent_point_id}")
def delete_agent_point(session: SessionDep, agent_point_id: int) -> Message:
    """
    Delete a agent_point.
    """
    agent_point = session.get(AgentPoint, agent_point_id)
    # statement = delete(Item).where(col(Item.owner_id) == agent_point_id)
    # session.exec(statement)
    session.delete(agent_point)
    session.commit()
    return Message(message="AgentPoint deleted successfully")
