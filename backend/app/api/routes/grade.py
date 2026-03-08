from typing import Any

from app.api.deps import SessionDep
from app.models import Grade, GradePublic, GradesPublic, Message
from fastapi import APIRouter
from sqlmodel import func, select

router = APIRouter(prefix="/grades", tags=["grades"])


@router.get(
    "/",
    response_model=GradesPublic,
)
def read_grades(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve grades.
    """

    count_statement = select(func.count()).select_from(Grade)
    count = session.exec(count_statement).one()

    statement = select(Grade).offset(skip).limit(limit)
    grades = session.exec(statement).all()

    return GradesPublic(data=grades, count=count)


@router.get("/{grade_id}", response_model=GradePublic)
def read_grade_by_id(grade_id: int, session: SessionDep) -> Any:
    """
    Get a specific grade by id.
    """
    grade = session.get(Grade, grade_id)
    return grade


@router.delete("/{grade_id}")
def delete_grade(session: SessionDep, grade_id: int) -> Message:
    """
    Delete a grade.
    """
    grade = session.get(Grade, grade_id)
    # statement = delete(Item).where(col(Item.owner_id) == grade_id)
    # session.exec(statement)
    session.delete(grade)
    session.commit()
    return Message(message="Grade deleted successfully")
