from typing import Any

from app.api.deps import EmployeeManagerUser, ManagerOrFieldEmployeeUser, SessionDep
from app.models import (
    Grade,
    GradeCreate,
    GradePublic,
    GradesPublic,
    GradeUpdate,
    Message,
)
from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

router = APIRouter(prefix="/grades", tags=["grades"])


@router.post("/", response_model=GradePublic)
def create_grade(
    *, session: SessionDep, _em: EmployeeManagerUser, grade_in: GradeCreate
) -> Any:
    """
    Create new grade.
    """
    grade = Grade.model_validate(grade_in)
    session.add(grade)
    session.commit()
    session.refresh(grade)
    return grade


@router.get(
    "/",
    response_model=GradesPublic,
)
def read_grades(
    session: SessionDep, _reader: ManagerOrFieldEmployeeUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve grades.
    """

    count_statement = select(func.count()).select_from(Grade)
    count = session.exec(count_statement).one()

    statement = select(Grade).offset(skip).limit(limit)
    grades = session.exec(statement).all()

    return GradesPublic(data=grades, count=count)


@router.get("/{grade_id}", response_model=GradePublic)
def read_grade_by_id(
    grade_id: int, session: SessionDep, _reader: ManagerOrFieldEmployeeUser
) -> Any:
    """
    Get a specific grade by id.
    """
    grade = session.get(Grade, grade_id)
    return grade


@router.put("/{id}", response_model=GradePublic)
def update_grade(
    *,
    session: SessionDep,
    _em: EmployeeManagerUser,
    id: int,
    grade_in: GradeUpdate,
) -> Any:
    """
    Update an grade.
    """
    grade = session.get(Grade, id)
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    update_dict = grade_in.model_dump(exclude_unset=True)
    grade.sqlmodel_update(update_dict)
    session.add(grade)
    session.commit()
    session.refresh(grade)
    return grade


@router.delete("/{grade_id}")
def delete_grade(session: SessionDep, _em: EmployeeManagerUser, grade_id: int) -> Message:
    """
    Delete a grade.
    """
    grade = session.get(Grade, grade_id)
    # statement = delete(Item).where(col(Item.owner_id) == grade_id)
    # session.exec(statement)
    session.delete(grade)
    session.commit()
    return Message(message="Grade deleted successfully")
