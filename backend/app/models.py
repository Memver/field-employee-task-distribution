import uuid
from datetime import datetime, timezone

from pydantic import EmailStr
from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


class RoleBase(SQLModel):
    name: str


class Role(RoleBase, table=True):
    id: int = Field(primary_key=True)


class GradeBase(SQLModel):
    name: str
    level: int


class Grade(GradeBase, table=True):
    id: int = Field(primary_key=True)


class LocationBase(SQLModel):
    address: str


class Location(LocationBase, table=True):
    id: int = Field(primary_key=True)


class PriorityBase(SQLModel):
    name: str
    level: int


class Priority(PriorityBase, table=True):
    id: int = Field(primary_key=True)


class TaskStatusBase(SQLModel):
    name: str


class TaskStatus(TaskStatusBase, table=True):
    id: int = Field(primary_key=True)


class UserBase(SQLModel):
    login: str
    name: str
    surname: str
    middle_name: str


class User(UserBase, table=True):
    id: int = Field(primary_key=True)
    role_id: int
    hashed_password: str


class EmployeeBase(SQLModel):
    pass


class Employee(EmployeeBase, table=True):
    id: int = Field(primary_key=True)
    user_id: int
    grade_id: int
    start_location_id: int


class TaskTypeBase(SQLModel):
    name: str
    execution_time: int


class TaskType(TaskTypeBase, table=True):
    id: int = Field(primary_key=True)
    min_grade_id: int
    priority_id: int


class AgentPointBase(SQLModel):
    created_time: datetime
    is_cards_delivered: bool
    days_since_last_card_gived: int
    approved_applications: int
    cards_gived: int


class AgentPoint(AgentPointBase, table=True):
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


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


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
