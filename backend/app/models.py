from typing import Optional
import uuid
from datetime import datetime, timezone

from pydantic import EmailStr
from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel
from sqlmodel import Column, Index, CheckConstraint, UniqueConstraint


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


class RoleBase(SQLModel):
    name: str = Field(
        max_length=64,
        unique=True,
        nullable=False,
    )


class Role(RoleBase, table=True):
    id: int = Field(primary_key=True)


class GradeBase(SQLModel):
    name: str = Field(max_length=64, unique=True, nullable=False)
    level: int = Field(gt=0, unique=True, nullable=False)


class Grade(GradeBase, table=True):
    id: int = Field(primary_key=True)


class LocationBase(SQLModel):
    address: str = Field(
        max_length=255,
        nullable=False,
    )
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)


class Location(LocationBase, table=True):
    id: int = Field(primary_key=True)


class PriorityBase(SQLModel):
    name: str = Field(max_length=32, unique=True, nullable=False)
    level: int = Field(gt=0, unique=True, nullable=False)


class Priority(PriorityBase, table=True):
    id: int = Field(primary_key=True)


class TaskStatusBase(SQLModel):
    name: str = Field(max_length=32, unique=True, nullable=False)


class TaskStatus(TaskStatusBase, table=True):
    __tablename__ = "task_status"

    id: int = Field(primary_key=True)


class UserBase(SQLModel):
    login: str = Field(
        min_length=3,
        max_length=32,
        unique=True,
        nullable=False,
    )
    name: str = Field(
        max_length=64,
        nullable=False,
    )
    surname: str = Field(
        max_length=64,
        nullable=False,
    )
    middle_name: str = Field(
        max_length=64,
        nullable=False,
    )


class User(UserBase, table=True):
    id: int = Field(primary_key=True)
    role_id: int = Field(
        foreign_key="role.id",
        nullable=False,
    )
    hashed_password: str


class EmployeeBase(SQLModel):
    pass


class Employee(EmployeeBase, table=True):
    id: int = Field(primary_key=True)
    user_id: int = Field(
        foreign_key="user.id",
        unique=True,
        nullable=False,
    )
    grade_id: int = Field(
        foreign_key="grade.id",
        nullable=False,
    )
    start_location_id: int = Field(
        foreign_key="location.id",
        nullable=False,
    )


class TaskTypeBase(SQLModel):
    name: str = Field(
        max_length=255,
        unique=True,
        nullable=False,
    )
    execution_time: int = Field(
        gt=0,
        nullable=False,
    )


class TaskType(TaskTypeBase, table=True):
    __tablename__ = "task_type"

    id: int = Field(primary_key=True)
    min_grade_id: int = Field(
        foreign_key="grade.id",
        nullable=False,
    )
    priority_id: int = Field(
        foreign_key="priority.id",
        nullable=False,
    )


class AgentPointBase(SQLModel):
    created_time: datetime
    is_cards_delivered: bool
    days_since_last_card_gived: int
    approved_applications: int
    cards_gived: int


class AgentPoint(AgentPointBase, table=True):
    __tablename__ = "agent_point"

    id: int = Field(primary_key=True)
    location_id: int


class TaskBase(SQLModel):
    start_time: datetime
    finish_time: datetime
    comment: str


class Task(TaskBase, table=True):
    id: int = Field(primary_key=True)
    employee_id: int
    task_type_id: int
    agent_point_id: int
    task_status_id: int


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)
