from typing import Any

from app.api.deps import CurrentUser, SessionDep
from app.core.security import get_password_hash
from app.models import (
    Message,
    UpdatePassword,
    User,
    UserCreate,
    UserPublic,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)
from fastapi import APIRouter
from sqlmodel import func, select

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    response_model=UsersPublic,
)
def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """

    count_statement = select(func.count()).select_from(User)
    count = session.exec(count_statement).one()

    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()

    return UsersPublic(data=users, count=count)


@router.post("/", response_model=UserPublic)
def create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
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


# @router.patch("/me", response_model=UserPublic)
# def update_user_me(
#     *, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser
# ) -> Any:
#     """
#     Update own user.
#     """
#     user_data = user_in.model_dump(exclude_unset=True)
#     current_user.sqlmodel_update(user_data)
#     session.add(current_user)
#     session.commit()
#     session.refresh(current_user)
#     return current_user


# @router.patch("/me/password", response_model=Message)
# def update_password_me(
#     *, session: SessionDep, body: UpdatePassword, current_user: CurrentUser
# ) -> Any:
#     """
#     Update own password.
#     """
#     hashed_password = get_password_hash(body.new_password)
#     current_user.hashed_password = hashed_password
#     session.add(current_user)
#     session.commit()
#     return Message(message="Password updated successfully")


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    return current_user


# @router.delete("/me", response_model=Message)
# def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Any:
#     """
#     Delete own user.
#     """
#     session.delete(current_user)
#     session.commit()
#     return Message(message="User deleted successfully")


@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(
    user_id: int, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific user by id.
    """
    user = session.get(User, user_id)
    return user


# @router.patch(
#     "/{user_id}",
#     response_model=UserPublic,
# )
# def update_user(
#     *,
#     session: SessionDep,
#     user_id: int,
#     user_in: UserUpdate,
# ) -> Any:
#     """
#     Update a user.
#     """

#     db_user = session.get(User, user_id)
#     user_data = user_in.model_dump(exclude_unset=True)
#     extra_data = {}
#     if "password" in user_data:
#         password = user_data["password"]
#         hashed_password = get_password_hash(password)
#         extra_data["hashed_password"] = hashed_password
#     db_user.sqlmodel_update(user_data, update=extra_data)
#     session.add(db_user)
#     session.commit()
#     session.refresh(db_user)
#     return db_user


@router.delete("/{user_id}")
def delete_user(
    session: SessionDep, current_user: CurrentUser, user_id: int
) -> Message:
    """
    Delete a user.
    """
    user = session.get(User, user_id)
    # statement = delete(Item).where(col(Item.owner_id) == user_id)
    # session.exec(statement)
    session.delete(user)
    session.commit()
    return Message(message="User deleted successfully")
