import uuid
from datetime import date, datetime, timezone
from typing import Optional

from pydantic import EmailStr, model_validator
from sqlmodel import (
    CheckConstraint,
    Column,
    Field,
    Relationship,
    SQLModel,
    UniqueConstraint,
)
from sqlalchemy import DateTime
from app.services.agent_point_event_schema import validate_agent_point_event_payload


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
    lat: Optional["float"] = Field(default=None, ge=-90, le=90)
    lon: Optional["float"] = Field(default=None, ge=-180, le=180)


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


class User(UserBase, table=True):
    id: int = Field(default=None, primary_key=True)
    role_id: int = Field(
        foreign_key="role.id",
        nullable=False,
    )
    hashed_password: str

    role: Optional["Role"] = Relationship()

    employee: Optional["Employee"] = Relationship(
        back_populates="user", cascade_delete=True
    )
    agent_point_manager: Optional["AgentPointManager"] = Relationship(
        back_populates="user", cascade_delete=True
    )


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

    user: Optional["User"] = Relationship(back_populates="employee")
    grade: Optional["Grade"] = Relationship()
    start_location: Optional["Location"] = Relationship()

    tasks: list[Optional["Task"]] = Relationship(back_populates="employee")


class TaskTypeBase(SQLModel):
    name: str = Field(
        max_length=255,
        unique=True,
        nullable=False,
    )
    execution_time: float = Field(
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

    min_grade: Optional["Grade"] = Relationship()
    priority: Optional["Priority"] = Relationship()


class AgentPointBase(SQLModel):
    created_time: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )


class AgentPoint(AgentPointBase, table=True):
    __tablename__ = "agent_point"

    id: int = Field(default=None, primary_key=True)
    location_id: int = Field(
        foreign_key="location.id",
        nullable=False,
    )

    location: Optional["Location"] = Relationship()

    tasks: list[Optional["Task"]] = Relationship(back_populates="agent_point")
    events: list[Optional["AgentPointEvent"]] = Relationship(back_populates="agent_point")
    managers: list[Optional["AgentPointManager"]] = Relationship(
        back_populates="agent_point"
    )


class AgentPointManagerBase(SQLModel):
    pass


class AgentPointManager(AgentPointManagerBase, table=True):
    __tablename__ = "agent_point_manager"

    id: int = Field(default=None, primary_key=True)
    agent_point_id: int = Field(
        foreign_key="agent_point.id",
        nullable=False,
        ondelete="CASCADE",
    )
    user_id: int = Field(
        foreign_key="user.id",
        unique=True,
        nullable=False,
        ondelete="CASCADE",
    )

    agent_point: Optional["AgentPoint"] = Relationship(back_populates="managers")
    user: Optional["User"] = Relationship(back_populates="agent_point_manager")


class AgentPointEventBase(SQLModel):
    event_time: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    event_type: str = Field(min_length=1, max_length=64, nullable=False)
    metric_name: str | None = Field(default=None, max_length=64)
    metric_delta: int | None = Field(default=None)
    metric_value_num: int | None = Field(default=None)
    metric_value_bool: bool | None = Field(default=None)

    @model_validator(mode="after")
    def validate_event_schema(self) -> "AgentPointEventBase":
        validate_agent_point_event_payload(
            event_type=self.event_type,
            metric_name=self.metric_name,
            metric_delta=self.metric_delta,
            metric_value_num=self.metric_value_num,
            metric_value_bool=self.metric_value_bool,
        )
        return self


class AgentPointEvent(AgentPointEventBase, table=True):
    __tablename__ = "agent_point_event"
    __table_args__ = (
        CheckConstraint(
            "metric_delta IS NOT NULL OR metric_value_num IS NOT NULL OR metric_value_bool IS NOT NULL",
            name="ck_agent_point_event_has_metric_value",
        ),
        CheckConstraint(
            "(CASE WHEN metric_delta IS NOT NULL THEN 1 ELSE 0 END + "
            "CASE WHEN metric_value_num IS NOT NULL THEN 1 ELSE 0 END + "
            "CASE WHEN metric_value_bool IS NOT NULL THEN 1 ELSE 0 END) = 1",
            name="ck_agent_point_event_exactly_one_metric_value",
        ),
        CheckConstraint("event_type <> ''", name="ck_agent_point_event_event_type_not_empty"),
        CheckConstraint(
            "("
            "(event_type = 'cards_delivery_status_changed' "
            "AND metric_name = 'is_cards_delivered' "
            "AND metric_value_bool IS NOT NULL)"
            " OR "
            "(event_type = 'approved_applications_changed' "
            "AND metric_name = 'approved_applications' "
            "AND metric_value_bool IS NULL)"
            " OR "
            "(event_type = 'cards_gived_changed' "
            "AND metric_name = 'cards_gived' "
            "AND metric_value_bool IS NULL)"
            ")",
            name="ck_agent_point_event_schema_pairs",
        ),
    )

    id: int = Field(default=None, primary_key=True)
    agent_point_id: int = Field(
        foreign_key="agent_point.id",
        nullable=False,
        ondelete="CASCADE",
    )

    agent_point: Optional["AgentPoint"] = Relationship(back_populates="events")


class TaskBase(SQLModel):
    start_time: datetime = Field(
        ge=datetime(2021, 1, 1),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    finish_time: datetime = Field(
        ge=datetime(2021, 1, 1),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
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
    ap_manager_confirmed: bool | None = Field(default=None)
    ap_manager_comment: str | None = Field(default=None, max_length=4096)
    ap_manager_user_id: int | None = Field(default=None, foreign_key="user.id")

    employee: Optional["Employee"] = Relationship(back_populates="tasks")
    task_type: Optional["TaskType"] = Relationship()
    agent_point: Optional["AgentPoint"] = Relationship(back_populates="tasks")
    task_status: Optional["TaskStatus"] = Relationship()
    ap_manager_user: Optional["User"] = Relationship()


class TaskCarryoverBase(SQLModel):
    carryover_days: int = Field(gt=0, nullable=False, default=1)
    planned_for_date: date = Field(nullable=False)
    source_reason: str = Field(min_length=1, max_length=1024, nullable=False)
    created_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class TaskCarryover(TaskCarryoverBase, table=True):
    __tablename__ = "task_carryover"
    __table_args__ = (
        UniqueConstraint(
            "agent_point_id",
            "task_type_id",
            "planned_for_date",
            name="uq_task_carryover_agent_point_task_type_planned_for_date",
        ),
    )

    id: int = Field(default=None, primary_key=True)
    agent_point_id: int = Field(
        foreign_key="agent_point.id",
        nullable=False,
        ondelete="CASCADE",
    )
    task_type_id: int = Field(
        foreign_key="task_type.id",
        nullable=False,
        ondelete="CASCADE",
    )

    agent_point: Optional["AgentPoint"] = Relationship()
    task_type: Optional["TaskType"] = Relationship()


class RoleCreate(RoleBase):
    pass


class RoleUpdate(RoleBase):
    pass


class RolePublic(RoleBase):
    id: int


class RolesPublic(SQLModel):
    data: list[RolePublic]
    count: int


class GradeCreate(GradeBase):
    pass


class GradeUpdate(GradeBase):
    pass


class GradePublic(GradeBase):
    id: int


class GradesPublic(SQLModel):
    data: list[GradePublic]
    count: int


class LocationCreate(LocationBase):
    pass


class LocationUpdate(LocationBase):
    pass


class LocationPublic(LocationBase):
    id: int


class LocationsPublic(SQLModel):
    data: list[LocationPublic]
    count: int


class PriorityCreate(PriorityBase):
    pass


class PriorityUpdate(PriorityBase):
    pass


class PriorityPublic(PriorityBase):
    id: int


class PrioritiesPublic(SQLModel):
    data: list[PriorityPublic]
    count: int


class TaskStatusCreate(TaskStatusBase):
    pass


class TaskStatusUpdate(TaskStatusBase):
    pass


class TaskStatusPublic(TaskStatusBase):
    id: int


class TaskStatusesPublic(SQLModel):
    data: list[TaskStatusPublic]
    count: int


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=1, max_length=128)
    role_id: int = Field(nullable=False)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    password: str | None = Field(default=None, min_length=1, max_length=128)
    role_id: int = Field(nullable=False)


class UserUpdateMe(SQLModel):
    full_name: Optional["str"] = Field(default=None, max_length=255)
    email: Optional["EmailStr"] = Field(default=None, max_length=255)


# Properties to return via API, id is always required
class UserRefPublic(SQLModel):
    id: int
    login: str
    name: str
    surname: str
    middle_name: str


class UserPublic(UserBase):
    id: int
    role: RolePublic


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class EmployeeCreate(EmployeeBase):
    user_id: int = Field(nullable=False)
    grade_id: int = Field(nullable=False)
    start_location_id: int = Field(nullable=False)


class EmployeeUpdate(EmployeeBase):
    user_id: int = Field(nullable=False)
    grade_id: int = Field(nullable=False)
    start_location_id: int = Field(nullable=False)


class EmployeePublic(EmployeeBase):
    id: int
    user_id: int = Field(nullable=False)
    grade_id: int = Field(nullable=False)
    start_location_id: int = Field(nullable=False)
    user: UserRefPublic
    grade: GradePublic
    start_location: LocationPublic


class EmployeesPublic(SQLModel):
    data: list[EmployeePublic]
    count: int


class TaskTypeCreate(TaskTypeBase):
    min_grade_id: int = Field(nullable=False)
    priority_id: int = Field(nullable=False)


class TaskTypeUpdate(TaskTypeBase):
    min_grade_id: int = Field(nullable=False)
    priority_id: int = Field(nullable=False)


class TaskTypePublic(TaskTypeBase):
    id: int
    min_grade_id: int = Field(nullable=False)
    priority_id: int = Field(nullable=False)
    min_grade: GradePublic
    priority: PriorityPublic


class TaskTypesPublic(SQLModel):
    data: list[TaskTypePublic]
    count: int


class AgentPointCreate(AgentPointBase):
    location_id: int = Field(nullable=False)


class AgentPointUpdate(AgentPointBase):
    location_id: int = Field(nullable=False)


class AgentPointPublic(AgentPointBase):
    id: int
    location: LocationPublic


class AgentPointsPublic(SQLModel):
    data: list[AgentPointPublic]
    count: int


class AgentPointEventCreate(AgentPointEventBase):
    agent_point_id: int = Field(nullable=False)


class AgentPointEventUpdate(AgentPointEventBase):
    agent_point_id: int = Field(nullable=False)


class AgentPointEventPublic(AgentPointEventBase):
    id: int
    agent_point_id: int = Field(nullable=False)
    agent_point: AgentPointPublic


class AgentPointEventsPublic(SQLModel):
    data: list[AgentPointEventPublic]
    count: int


class TaskCreate(TaskBase):
    employee_id: int = Field(nullable=False)
    task_type_id: int = Field(nullable=False)
    agent_point_id: int = Field(nullable=False)
    task_status_id: int = Field(nullable=False)


class TaskUpdate(TaskBase):
    employee_id: int = Field(nullable=False)
    task_type_id: int = Field(nullable=False)
    agent_point_id: int = Field(nullable=False)
    task_status_id: int = Field(nullable=False)


class TaskSelfUpdate(SQLModel):
    """Обновление статуса и комментария выездным сотрудником к своей задаче."""

    task_status_id: int = Field(nullable=False)
    comment: str | None = Field(default=None, max_length=4096)


class TaskCompleteUpdate(SQLModel):
    """Отметка задачи как выполненной с опциональным комментарием."""

    comment: str | None = Field(default=None, max_length=4096)


class TaskAgentPointManagerConfirmUpdate(SQLModel):
    """Решение менеджера агентской точки по выполненной задаче."""

    confirmed: bool = Field(nullable=False)
    comment: str | None = Field(default=None, max_length=4096)


class TaskSkipUpdate(SQLModel):
    """Пропуск задачи с обязательным комментарием причины."""

    comment: str = Field(min_length=1, max_length=4096)


class TaskPublic(TaskBase):
    id: int
    employee_id: int = Field(nullable=False)
    task_type_id: int = Field(nullable=False)
    agent_point_id: int = Field(nullable=False)
    task_status_id: int = Field(nullable=False)
    employee: EmployeePublic
    task_type: TaskTypePublic
    agent_point: AgentPointPublic
    task_status: TaskStatusPublic


class TasksPublic(SQLModel):
    data: list[TaskPublic]
    count: int


class TaskMePublic(TaskBase):
    id: int
    agent_point: AgentPointPublic


class TasksMePublic(SQLModel):
    tasks: list[TaskMePublic]
    route: list[list[float]] | None = None
    start_location: LocationPublic


class DistributionAssignmentPublic(SQLModel):
    employee_id: int
    employee_full_name: str
    agent_point_id: int
    agent_point_address: str | None
    task_type_id: int
    task_type_name: str
    day_index: int
    start_time: datetime
    finish_time: datetime
    reason: str


class DistributionUnplacedPublic(SQLModel):
    agent_point_id: int
    agent_point_address: str | None
    task_type_id: int | None
    task_type_name: str | None
    reason: str


class DistributionReportPublic(SQLModel):
    message: str
    assignments: list[DistributionAssignmentPublic]
    unplaced: list[DistributionUnplacedPublic]


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: Optional["str"] = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)
