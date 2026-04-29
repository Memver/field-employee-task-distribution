from typing import Any

from app.api.deps import AgentPointReaderUser, AgentPointTableEditorUser, SessionDep
from app.core.roles import is_agent_point_manager_user
from app.models import (
    AgentPointManager,
    AgentPointEvent,
    AgentPointEventCreate,
    AgentPointEventPublic,
    AgentPointEventsPublic,
    AgentPointEventUpdate,
    Message,
)
from fastapi import APIRouter, HTTPException
from sqlmodel import func, select
from app.repositories import agent_point_event as event_repository
from app.services import agent_point_event_service

router = APIRouter(prefix="/agent-point-events", tags=["agent-point-events"])


@router.post("/", response_model=AgentPointEventPublic)
def create_agent_point_event(
    *,
    session: SessionDep,
    editor: AgentPointTableEditorUser,
    agent_point_event_in: AgentPointEventCreate,
) -> Any:
    """
    Create new agent_point_event.
    """
    allowed_agent_point_ids = _get_allowed_agent_point_ids_for_ap_manager(
        session=session, user_id=editor.id, role=editor.role
    )
    if (
        allowed_agent_point_ids is not None
        and agent_point_event_in.agent_point_id not in allowed_agent_point_ids
    ):
        raise HTTPException(
            status_code=403,
            detail="Недостаточно прав для изменения событий этой агентской точки",
        )
    return agent_point_event_service.create_event(
        session=session, payload=agent_point_event_in
    )


@router.get("/", response_model=AgentPointEventsPublic)
def read_agent_point_events(
    session: SessionDep,
    reader: AgentPointReaderUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve agent_point_events.
    """
    allowed_agent_point_ids = _get_allowed_agent_point_ids_for_ap_manager(
        session=session, user_id=reader.id, role=reader.role
    )
    if allowed_agent_point_ids is None:
        count_statement = select(func.count()).select_from(AgentPointEvent)
        count = session.exec(count_statement).one()
        statement = select(AgentPointEvent).offset(skip).limit(limit)
        agent_point_events = session.exec(statement).all()
    else:
        count = event_repository.count_for_agent_points(
            session=session, agent_point_ids=allowed_agent_point_ids
        )
        agent_point_events = event_repository.list_for_agent_points(
            session=session,
            agent_point_ids=allowed_agent_point_ids,
            skip=skip,
            limit=limit,
        )

    return AgentPointEventsPublic(data=agent_point_events, count=count)


@router.get("/{agent_point_event_id}", response_model=AgentPointEventPublic)
def read_agent_point_event_by_id(
    agent_point_event_id: int, session: SessionDep, reader: AgentPointReaderUser
) -> Any:
    """
    Get a specific agent_point_event by id.
    """
    allowed_agent_point_ids = _get_allowed_agent_point_ids_for_ap_manager(
        session=session, user_id=reader.id, role=reader.role
    )
    if allowed_agent_point_ids is None:
        agent_point_event = event_repository.get_by_id(
            session=session, event_id=agent_point_event_id
        )
    else:
        agent_point_event = event_repository.get_by_id_for_agent_points(
            session=session,
            event_id=agent_point_event_id,
            agent_point_ids=allowed_agent_point_ids,
        )
    if not agent_point_event:
        raise HTTPException(status_code=404, detail="AgentPointEvent not found")
    return agent_point_event


@router.put("/{id}", response_model=AgentPointEventPublic)
def update_agent_point_event(
    *,
    session: SessionDep,
    editor: AgentPointTableEditorUser,
    id: int,
    agent_point_event_in: AgentPointEventUpdate,
) -> Any:
    """
    Update an agent_point_event.
    """
    allowed_agent_point_ids = _get_allowed_agent_point_ids_for_ap_manager(
        session=session, user_id=editor.id, role=editor.role
    )
    if (
        allowed_agent_point_ids is not None
        and agent_point_event_in.agent_point_id not in allowed_agent_point_ids
    ):
        raise HTTPException(
            status_code=403,
            detail="Недостаточно прав для изменения событий этой агентской точки",
        )
    if allowed_agent_point_ids is None:
        agent_point_event = event_repository.get_by_id(session=session, event_id=id)
    else:
        agent_point_event = event_repository.get_by_id_for_agent_points(
            session=session, event_id=id, agent_point_ids=allowed_agent_point_ids
        )
    if not agent_point_event:
        raise HTTPException(status_code=404, detail="AgentPointEvent not found")
    return agent_point_event_service.update_event(
        session=session, event=agent_point_event, payload=agent_point_event_in
    )


@router.delete("/{agent_point_event_id}")
def delete_agent_point_event(
    session: SessionDep,
    editor: AgentPointTableEditorUser,
    agent_point_event_id: int,
) -> Message:
    """
    Delete a agent_point_event.
    """
    allowed_agent_point_ids = _get_allowed_agent_point_ids_for_ap_manager(
        session=session, user_id=editor.id, role=editor.role
    )
    if allowed_agent_point_ids is None:
        agent_point_event = event_repository.get_by_id(
            session=session, event_id=agent_point_event_id
        )
    else:
        agent_point_event = event_repository.get_by_id_for_agent_points(
            session=session,
            event_id=agent_point_event_id,
            agent_point_ids=allowed_agent_point_ids,
        )
    if not agent_point_event:
        raise HTTPException(status_code=404, detail="AgentPointEvent not found")
    session.delete(agent_point_event)
    session.commit()
    return Message(message="AgentPointEvent deleted successfully")


def _get_allowed_agent_point_ids_for_ap_manager(
    *, session: SessionDep, user_id: int, role: object | None
) -> list[int] | None:
    if not is_agent_point_manager_user(role):
        return None
    return session.exec(
        select(AgentPointManager.agent_point_id).where(AgentPointManager.user_id == user_id)
    ).all()
