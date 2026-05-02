from typing import Any

from app.api.deps import AdminUser, CurrentUser, SessionDep
from app.core.roles import is_admin_user
from app.core.security import get_password_hash
from app.models import (
    Message,
    User,
    UserCreate,
    UserPublic,
    UsersPublic,
    UserUpdate,
)
from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserPublic)
def create_user(
    *, session: SessionDep, _admin: AdminUser, user_in: UserCreate
) -> Any:
    """
    Create new user.
    """
    user = User.model_validate(
        user_in, update={"hashed_password": get_password_hash(user_in.password)}
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get(
    "/",
    response_model=UsersPublic,
)
def read_users(
    session: SessionDep, _admin: AdminUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve users.
    """

    count_statement = select(func.count()).select_from(User)
    count = session.exec(count_statement).one()

    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()

    return UsersPublic(data=users, count=count)


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    user = UserPublic.model_validate(current_user)
    return user


@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(
    user_id: int, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific user by id.
    """
    if not is_admin_user(current_user.role) and current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Недостаточно прав для просмотра этого пользователя",
        )
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put(
    "/{id}",
    response_model=UserPublic,
)
def update_user(
    *,
    session: SessionDep,
    _admin: AdminUser,
    id: int,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user.
    """

    db_user = session.get(User, id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )

    user_data = user_in.model_dump(exclude_unset=True)

    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password

    db_user.sqlmodel_update(user_data, update=extra_data)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.delete("/{user_id}")
def delete_user(session: SessionDep, _admin: AdminUser, user_id: int) -> Message:
    """
    Delete a user.
    """
    user = session.get(User, user_id)
    session.delete(user)
    session.commit()
    return Message(message="User deleted successfully")
