from typing import Any

from app.api.deps import SessionDep
from app.models import Message, Role, RolePublic, RolesPublic
from fastapi import APIRouter
from sqlmodel import func, select

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get(
    "/",
    response_model=RolesPublic,
)
def read_roles(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve roles.
    """

    count_statement = select(func.count()).select_from(Role)
    count = session.exec(count_statement).one()

    statement = select(Role).offset(skip).limit(limit)
    roles = session.exec(statement).all()

    return RolesPublic(data=roles, count=count)


@router.get("/{role_id}", response_model=RolePublic)
def read_role_by_id(role_id: int, session: SessionDep) -> Any:
    """
    Get a specific role by id.
    """
    role = session.get(Role, role_id)
    return role


@router.delete("/{role_id}")
def delete_role(session: SessionDep, role_id: int) -> Message:
    """
    Delete a role.
    """
    role = session.get(Role, role_id)
    # statement = delete(Item).where(col(Item.owner_id) == role_id)
    # session.exec(statement)
    session.delete(role)
    session.commit()
    return Message(message="Role deleted successfully")
