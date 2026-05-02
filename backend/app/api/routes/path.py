from typing import Any

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import (
    User,
    UsersPublic,
)
from fastapi import APIRouter, Depends
from sqlmodel import func, select

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """

    count_statement = select(func.count()).select_from(User)
    count = session.exec(count_statement).one()

    statement = select(User).order_by(User.created_at.desc()).offset(skip).limit(limit)
    users = session.exec(statement).all()

    return UsersPublic(data=users, count=count)
