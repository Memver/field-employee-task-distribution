from typing import Any

from app.api.deps import AdminUser, CurrentUser, SessionDep
from app.core.roles import is_admin_user
from app.models import Message, Role, RoleCreate, RolePublic, RoleUpdate, RolesPublic
from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

router = APIRouter(prefix="/roles", tags=["roles"])


@router.post("/", response_model=RolePublic)
def create_role(*, session: SessionDep, _admin: AdminUser, role_in: RoleCreate) -> Any:
    """
    Create new role.
    """
    role = Role.model_validate(role_in)
    session.add(role)
    session.commit()
    session.refresh(role)
    return role


@router.get(
    "/",
    response_model=RolesPublic,
)
def read_roles(
    session: SessionDep, _admin: AdminUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve roles.
    """

    count_statement = select(func.count()).select_from(Role)
    count = session.exec(count_statement).one()

    statement = select(Role).offset(skip).limit(limit)
    roles = session.exec(statement).all()

    return RolesPublic(data=roles, count=count)


@router.get("/{role_id}", response_model=RolePublic)
def read_role_by_id(
    role_id: int, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific role by id.
    ADMIN — любая роль; остальные — только своя (role_id == current_user.role_id).
    """
    if is_admin_user(current_user.role) or current_user.role_id == role_id:
        role = session.get(Role, role_id)
        if role is None:
            raise HTTPException(status_code=404, detail="Role not found")
        return role
    raise HTTPException(
        status_code=403,
        detail="Недостаточно прав для просмотра этой роли",
    )


@router.put("/{id}", response_model=RolePublic)
def update_role(
    *,
    session: SessionDep,
    _admin: AdminUser,
    id: int,
    role_in: RoleUpdate,
) -> Any:
    """
    Update an role.
    """
    role = session.get(Role, id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    update_dict = role_in.model_dump(exclude_unset=True)
    role.sqlmodel_update(update_dict)
    session.add(role)
    session.commit()
    session.refresh(role)
    return role


@router.delete("/{role_id}")
def delete_role(session: SessionDep, _admin: AdminUser, role_id: int) -> Message:
    """
    Delete a role.
    """
    role = session.get(Role, role_id)
    session.delete(role)
    session.commit()
    return Message(message="Role deleted successfully")
