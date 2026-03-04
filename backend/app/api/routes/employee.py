from typing import Any

from app.api.deps import SessionDep
from app.models import Employee, EmployeePublic, EmployeesPublic, Message
from fastapi import APIRouter
from sqlmodel import func, select

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get(
    "/",
    response_model=EmployeesPublic,
)
def read_employees(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve employees.
    """

    count_statement = select(func.count()).select_from(Employee)
    count = session.exec(count_statement).one()

    statement = select(Employee).offset(skip).limit(limit)
    employees = session.exec(statement).all()

    return EmployeesPublic(data=employees, count=count)


@router.get("/{employee_id}", response_model=EmployeePublic)
def read_employee_by_id(employee_id: int, session: SessionDep) -> Any:
    """
    Get a specific employee by id.
    """
    employee = session.get(Employee, employee_id)
    return employee


@router.delete("/{employee_id}")
def delete_employee(session: SessionDep, employee_id: int) -> Message:
    """
    Delete a employee.
    """
    employee = session.get(Employee, employee_id)
    # statement = delete(Item).where(col(Item.owner_id) == employee_id)
    # session.exec(statement)
    session.delete(employee)
    session.commit()
    return Message(message="Employee deleted successfully")
