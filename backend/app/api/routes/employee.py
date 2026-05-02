from typing import Any

from app.api.deps import EmployeeManagerUser, ManagerOrFieldEmployeeUser, SessionDep
from app.models import (
    Employee,
    EmployeeCreate,
    EmployeePublic,
    EmployeesPublic,
    EmployeeUpdate,
    Message,
)
from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

router = APIRouter(prefix="/employees", tags=["employees"])


@router.post("/", response_model=EmployeePublic)
def create_employee(
    *, session: SessionDep, _em: EmployeeManagerUser, employee_in: EmployeeCreate
) -> Any:
    """
    Create new employee.
    """
    employee = Employee.model_validate(employee_in)
    session.add(employee)
    session.commit()
    session.refresh(employee)
    return employee


@router.get(
    "/",
    response_model=EmployeesPublic,
)
def read_employees(
    session: SessionDep, _reader: ManagerOrFieldEmployeeUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve employees.
    """

    count_statement = select(func.count()).select_from(Employee)
    count = session.exec(count_statement).one()

    statement = select(Employee).offset(skip).limit(limit)
    employees = session.exec(statement).all()

    return EmployeesPublic(data=employees, count=count)


@router.get("/{employee_id}", response_model=EmployeePublic)
def read_employee_by_id(
    employee_id: int, session: SessionDep, _reader: ManagerOrFieldEmployeeUser
) -> Any:
    """
    Get a specific employee by id.
    """
    employee = session.get(Employee, employee_id)
    return employee


@router.put("/{id}", response_model=EmployeePublic)
def update_employee(
    *,
    session: SessionDep,
    _em: EmployeeManagerUser,
    id: int,
    employee_in: EmployeeUpdate,
) -> Any:
    """
    Update an employee.
    """
    employee = session.get(Employee, id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    update_dict = employee_in.model_dump(exclude_unset=True)
    employee.sqlmodel_update(update_dict)
    session.add(employee)
    session.commit()
    session.refresh(employee)
    return employee


@router.delete("/{employee_id}")
def delete_employee(
    session: SessionDep, _em: EmployeeManagerUser, employee_id: int
) -> Message:
    """
    Delete a employee.
    """
    employee = session.get(Employee, employee_id)
    # statement = delete(Item).where(col(Item.owner_id) == employee_id)
    # session.exec(statement)
    session.delete(employee)
    session.commit()
    return Message(message="Employee deleted successfully")
