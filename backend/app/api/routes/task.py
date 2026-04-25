from typing import Any

from app.api.deps import (
    AgentPointManagerUser,
    CurrentUser,
    EmployeeManagerUser,
    FieldEmployeeUser,
    SessionDep,
    ensure_field_employee_task_access,
)
from app.core.roles import is_employee_manager_user, is_field_employee_user
from app.models import (
    Message,
    TaskCompleteUpdate,
    TaskSkipUpdate,
    Task,
    TaskAgentPointManagerConfirmUpdate,
    TaskCreate,
    TaskPublic,
    TaskSelfUpdate,
    TasksMePublic,
    TasksPublic,
    TaskUpdate,
)
from fastapi import APIRouter, HTTPException
from sqlmodel import func, select
from app.repositories import task as task_repository
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskPublic)
def create_task(
    *, session: SessionDep, _em: EmployeeManagerUser, task_in: TaskCreate
) -> Any:
    """
    Create new task.
    """
    task = Task.model_validate(task_in)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.post("/distribute")
def distribute_tasks(*, session: SessionDep, _em: EmployeeManagerUser) -> Message:
    # Контекст: распределение использует матрицы расстояний/времени, а /tasks/me строит маршрут.
    # Детали интеграции с OSRM вынесены в сервисный слой (task_service + routing gateway).
    return task_service.distribute_tasks(session=session)


@router.get(
    "/",
    response_model=TasksPublic,
)
def read_tasks(
    session: SessionDep, _em: EmployeeManagerUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve tasks.
    """

    count_statement = select(func.count()).select_from(Task)
    count = session.exec(count_statement).one()

    statement = select(Task).offset(skip).limit(limit)
    tasks = session.exec(statement).all()

    return TasksPublic(data=tasks, count=count)


@router.get("/me", response_model=TasksMePublic)
def read_tasks_me(
    session: SessionDep,
    field_user: FieldEmployeeUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve my tasks with route path from start location through all tasks and back.
    """
    current_employee = field_user.employee
    return task_service.read_tasks_me(
        session=session,
        employee_id=current_employee.id,
        start_location_id=current_employee.start_location_id,
        skip=skip,
        limit=limit,
    )


@router.patch("/{task_id}/self", response_model=TaskPublic)
def update_my_task_status(
    *,
    session: SessionDep,
    field_user: FieldEmployeeUser,
    task_id: int,
    body: TaskSelfUpdate,
) -> Any:
    """
    Выездной сотрудник: смена статуса и комментария только по своей задаче.
    """
    task = task_repository.get_by_id(session=session, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    ensure_field_employee_task_access(
        field_user=field_user, task_employee_id=task.employee_id
    )
    task.task_status_id = body.task_status_id
    if body.comment is not None:
        task.comment = body.comment
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.patch("/{task_id}/complete", response_model=TaskPublic)
def complete_my_task(
    *,
    session: SessionDep,
    field_user: FieldEmployeeUser,
    task_id: int,
    body: TaskCompleteUpdate,
) -> Any:
    """
    Выездной сотрудник: отметить свою задачу как выполненную.
    """
    task = task_repository.get_by_id(session=session, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    ensure_field_employee_task_access(
        field_user=field_user, task_employee_id=task.employee_id
    )

    return task_service.mark_task_completed(session=session, task=task, comment=body.comment)


@router.patch("/{task_id}/skip", response_model=TaskPublic)
def skip_my_task(
    *,
    session: SessionDep,
    field_user: FieldEmployeeUser,
    task_id: int,
    body: TaskSkipUpdate,
) -> Any:
    """
    Выездной сотрудник: пропустить свою задачу с указанием причины.
    """
    task = task_repository.get_by_id(session=session, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    ensure_field_employee_task_access(
        field_user=field_user, task_employee_id=task.employee_id
    )

    return task_service.mark_task_skipped(session=session, task=task, comment=body.comment)


@router.patch("/{task_id}/complete-by-agent-point-manager", response_model=TaskPublic)
def complete_task_by_agent_point_manager(
    *,
    session: SessionDep,
    apm: AgentPointManagerUser,
    task_id: int,
    body: TaskAgentPointManagerConfirmUpdate,
) -> Any:
    """
    Менеджер агентской точки: подтвердить или отклонить статус задачи.
    """
    task = task_repository.get_by_id(session=session, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task_service.confirm_task_by_ap_manager(
        session=session,
        task=task,
        ap_manager_id=apm.id,
        confirmed=body.confirmed,
        comment=body.comment,
    )


@router.get("/{task_id}", response_model=TaskPublic)
def read_task_by_id(
    task_id: int, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific task by id.
    """
    task = task_repository.get_by_id(session=session, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if is_employee_manager_user(current_user.role):
        return task
    if (
        is_field_employee_user(current_user.role)
        and current_user.employee is not None
        and task.employee_id == current_user.employee.id
    ):
        return task
    raise HTTPException(
        status_code=403,
        detail="Недостаточно прав для просмотра этой задачи",
    )


@router.put("/{id}", response_model=TaskPublic)
def update_task(
    *,
    session: SessionDep,
    _em: EmployeeManagerUser,
    id: int,
    task_in: TaskUpdate,
) -> Any:
    """
    Update an task.
    """
    task = session.get(Task, id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    update_dict = task_in.model_dump(exclude_unset=True)
    task.sqlmodel_update(update_dict)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.delete("/{task_id}")
def delete_task(
    session: SessionDep, _em: EmployeeManagerUser, task_id: int
) -> Message:
    """
    Delete a task.
    """
    task = task_repository.get_by_id(session=session, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    # statement = delete(Item).where(col(Item.owner_id) == task_id)
    # session.exec(statement)
    session.delete(task)
    session.commit()
    return Message(message="Task deleted successfully")
