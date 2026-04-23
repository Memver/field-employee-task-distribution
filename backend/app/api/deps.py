from collections.abc import Generator
from typing import Annotated

import jwt
from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.core.roles import (
    DETAIL_ADMIN_ONLY_USERS_ROLES,
    DETAIL_APM_ONLY_AGENT_POINTS,
    is_admin_user,
    is_agent_point_manager_user,
    is_agent_point_table_editor,
    is_employee_manager_user,
    is_field_employee_user,
)
from app.models import TokenPayload, User
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlalchemy.orm import joinedload
from sqlmodel import Session

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(
        User, token_data.sub, options=[joinedload(User.role), joinedload(User.employee)]
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_admin_user(current_user: CurrentUser) -> User:
    if not is_admin_user(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуется роль ADMIN",
        )
    return current_user


AdminUser = Annotated[User, Depends(get_admin_user)]


def get_employee_manager_user(current_user: CurrentUser) -> User:
    if not is_employee_manager_user(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуется роль EMPLOYEE_MANAGER",
        )
    return current_user


EmployeeManagerUser = Annotated[User, Depends(get_employee_manager_user)]


def get_agent_point_table_editor_user(current_user: CurrentUser) -> User:
    if not is_agent_point_table_editor(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуется роль EMPLOYEE_MANAGER или AGENT_POINT_MANAGER",
        )
    return current_user


AgentPointTableEditorUser = Annotated[User, Depends(get_agent_point_table_editor_user)]


def get_agent_point_manager_user(current_user: CurrentUser) -> User:
    if not is_agent_point_manager_user(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуется роль AGENT_POINT_MANAGER",
        )
    return current_user


AgentPointManagerUser = Annotated[User, Depends(get_agent_point_manager_user)]


def get_manager_or_field_employee_user(current_user: CurrentUser) -> User:
    """
    EMPLOYEE_MANAGER или FIELD_EMPLOYEE: доступ к данным вне users/roles.
    ADMIN и AGENT_POINT_MANAGER сюда не допускаются.
    """
    if is_admin_user(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=DETAIL_ADMIN_ONLY_USERS_ROLES,
        )
    if is_agent_point_manager_user(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=DETAIL_APM_ONLY_AGENT_POINTS,
        )
    if is_employee_manager_user(current_user.role) or is_field_employee_user(
        current_user.role
    ):
        return current_user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Недостаточно прав",
    )


ManagerOrFieldEmployeeUser = Annotated[User, Depends(get_manager_or_field_employee_user)]


def get_agent_point_reader_user(current_user: CurrentUser) -> User:
    """Чтение agent_point: все кроме ADMIN (в т.ч. AGENT_POINT_MANAGER, FIELD_EMPLOYEE, EMPLOYEE_MANAGER)."""
    if is_admin_user(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=DETAIL_ADMIN_ONLY_USERS_ROLES,
        )
    if (
        is_employee_manager_user(current_user.role)
        or is_agent_point_manager_user(current_user.role)
        or is_field_employee_user(current_user.role)
    ):
        return current_user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Недостаточно прав",
    )


AgentPointReaderUser = Annotated[User, Depends(get_agent_point_reader_user)]


def get_field_employee_user(current_user: CurrentUser) -> User:
    if not is_field_employee_user(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступно только выездным сотрудникам",
        )
    if current_user.employee is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У пользователя нет профиля сотрудника",
        )
    return current_user


FieldEmployeeUser = Annotated[User, Depends(get_field_employee_user)]
