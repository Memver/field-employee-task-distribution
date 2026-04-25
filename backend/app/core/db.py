from pathlib import Path

from app.core.config import settings
from app.core.constants import TaskStatusName
from app.models import User
from app.repositories import task_status as task_status_repository
from sqlmodel import Session, create_engine, select, text

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def init_db(session: Session) -> None:
    from sqlmodel import SQLModel

    SQLModel.metadata.create_all(engine)

    users = session.exec(select(User).limit(2)).all()
    if not users:
        sql_path = Path(__file__).resolve().parents[1] / "db" / "db.sql"
        with open(sql_path, "r", encoding="utf-8") as file:
            sql_script = file.read()

        session.exec(text(sql_script))
        session.commit()
    _ensure_required_task_statuses(session=session)
    # role = session.exec(select(Role).where(Role.name == "ADMIN")).first()
    # if not role:
    #     role = Role(name="ADMIN")
    #     session.add(role)
    #     session.commit()
    #     session.refresh(role)

    # user = session.exec(
    #     select(User).where(User.login == settings.FIRST_SUPERUSER)
    # ).first()
    # if not user:
    #     user_in = UserCreate(
    #         login=settings.FIRST_SUPERUSER,
    #         password=settings.FIRST_SUPERUSER_PASSWORD,
    #         name="a",
    #         surname="a",
    #         middle_name="a",
    #         is_superuser=True,
    #         role_id=1,
    #     )
    #     user = user_service.create(session=session, user_create=user_in)


def _ensure_required_task_statuses(*, session: Session) -> None:
    for status_name in (
        TaskStatusName.ASSIGNED.value,
        TaskStatusName.COMPLETED.value,
        TaskStatusName.SKIPPED.value,
    ):
        task_status_repository.ensure_exists(session=session, name=status_name)
