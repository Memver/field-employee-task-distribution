import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import EmailStr
from sqlalchemy import DateTime
from sqlmodel import (
    CheckConstraint,
    Column,
    Field,
    Index,
    Relationship,
    SQLModel,
    UniqueConstraint,
)


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


class RoleBase(SQLModel):
    name: str = Field(
        max_length=64,
        unique=True,
        nullable=False,
    )


class Role(RoleBase, table=True):
    id: int = Field(default=None, primary_key=True)


class GradeBase(SQLModel):
    name: str = Field(max_length=64, unique=True, nullable=False)
    level: int = Field(gt=0, unique=True, nullable=False)


class Grade(GradeBase, table=True):
    id: int = Field(default=None, primary_key=True)


class LocationBase(SQLModel):
    address: str = Field(
        max_length=255,
        nullable=False,
    )
    lat: float | None = Field(default=None, ge=-90, le=90)
    lon: float | None = Field(default=None, ge=-180, le=180)


class Location(LocationBase, table=True):
    id: int = Field(default=None, primary_key=True)


class PriorityBase(SQLModel):
    name: str = Field(max_length=32, unique=True, nullable=False)
    level: int = Field(gt=0, unique=True, nullable=False)


class Priority(PriorityBase, table=True):
    id: int = Field(default=None, primary_key=True)


class TaskStatusBase(SQLModel):
    name: str = Field(max_length=32, unique=True, nullable=False)


class TaskStatus(TaskStatusBase, table=True):
    __tablename__ = "task_status"

    id: int = Field(default=None, primary_key=True)


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
    is_superuser: bool = False


# TODO: написать ondelete для каждого foreign_key.


class User(UserBase, table=True):
    id: int = Field(default=None, primary_key=True)
    role_id: int = Field(
        foreign_key="role.id",
        nullable=False,
    )
    hashed_password: str

    role: Role = Relationship()


class EmployeeBase(SQLModel):
    pass


class Employee(EmployeeBase, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(
        foreign_key="user.id", unique=True, nullable=False, ondelete="CASCADE"
    )
    grade_id: int = Field(
        foreign_key="grade.id",
        nullable=False,
    )
    start_location_id: int = Field(
        foreign_key="location.id",
        nullable=False,
    )

    user: User = Relationship(back_populates="employee")
    grade: Grade = Relationship()
    start_location: Location = Relationship()


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

    id: int = Field(default=None, primary_key=True)
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
    days_since_last_card_gived: int = Field(
        ge=0,
        nullable=False,
    )
    approved_applications: int = Field(
        ge=0,
        nullable=False,
    )
    cards_gived: int = Field(
        ge=0,
        nullable=False,
    )


class AgentPoint(AgentPointBase, table=True):
    __tablename__ = "agent_point"

    id: int = Field(default=None, primary_key=True)
    location_id: int = Field(
        foreign_key="location.id",
        nullable=False,
    )


class TaskBase(SQLModel):
    start_time: datetime = Field(ge=datetime(2021, 1, 1))
    finish_time: datetime = Field(ge=datetime(2021, 1, 1))
    comment: str = Field(
        max_length=4096,
    )


class Task(TaskBase, table=True):
    id: int = Field(default=None, primary_key=True)
    employee_id: int = Field(
        foreign_key="employee.id",
        nullable=False,
    )
    task_type_id: int = Field(
        foreign_key="task_type.id",
        nullable=False,
    )
    agent_point_id: int = Field(
        foreign_key="agent_point.id",
        nullable=False,
    )
    task_status_id: int = Field(
        foreign_key="task_status.id",
        nullable=False,
    )


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=1, max_length=128)
    role_id: int = Field(
        foreign_key="role.id",
        nullable=False,
    )


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


class RolePublic(RoleBase):
    id: int


class RolesPublic(SQLModel):
    data: list[RolePublic]
    count: int


class GradePublic(GradeBase):
    id: int


class GradesPublic(SQLModel):
    data: list[GradePublic]
    count: int


class LocationPublic(LocationBase):
    id: int


class LocationsPublic(SQLModel):
    data: list[LocationPublic]
    count: int


class PriorityPublic(PriorityBase):
    id: int


class PrioritiesPublic(SQLModel):
    data: list[PriorityPublic]
    count: int


class TaskStatusPublic(TaskStatusBase):
    id: int


class TaskStatusesPublic(SQLModel):
    data: list[TaskStatusPublic]
    count: int


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: int


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class EmployeePublic(EmployeeBase):
    id: int
    user_id: int
    grade_id: int
    start_location_id: int


class EmployeesPublic(SQLModel):
    data: list[EmployeePublic]
    count: int


class TaskTypePublic(TaskTypeBase):
    id: int
    min_grade_id: int
    priority_id: int


class TaskTypesPublic(SQLModel):
    data: list[TaskTypePublic]
    count: int


class AgentPointPublic(AgentPointBase):
    id: int
    location_id: int


class AgentPointsPublic(SQLModel):
    data: list[AgentPointPublic]
    count: int


class TaskPublic(TaskBase):
    id: int
    employee_id: int
    task_type_id: int
    agent_point_id: int
    task_status_id: int


class TasksPublic(SQLModel):
    data: list[TaskPublic]
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
