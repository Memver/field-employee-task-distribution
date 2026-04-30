from pathlib import Path
from datetime import date, timedelta

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
        _shift_agent_point_dates_to_today(session=session)
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





def _shift_agent_point_dates_to_today(*, session: Session) -> None:
    """
    Смещает даты подключения точек из датасета так, чтобы "вчера"
    из исходного среза стало вчера относительно текущего дня.
    """
    reference_yesterday = date(2023, 1, 2)
    target_yesterday = date.today() - timedelta(days=1)
    shift_days = (target_yesterday - reference_yesterday).days
    if shift_days == 0:
        return

    stmt = text(
        """
        UPDATE public.agent_point
        SET created_time = created_time + (:shift_interval * INTERVAL '1 day')
        """
    ).bindparams(shift_interval=shift_days)
    session.exec(stmt)

    event_stmt = text(
        """
        UPDATE public.agent_point_event
        SET event_time = event_time + (:shift_interval * INTERVAL '1 day')
        WHERE metric_name = 'cards_gived'
          AND event_type = 'cards_gived_changed'
        """
    ).bindparams(shift_interval=shift_days)
    session.exec(event_stmt)


def _ensure_required_task_statuses(*, session: Session) -> None:
    for status_name in (
        TaskStatusName.ASSIGNED.value,
        TaskStatusName.COMPLETED.value,
        TaskStatusName.SKIPPED.value,
    ):
        task_status_repository.ensure_exists(session=session, name=status_name)
