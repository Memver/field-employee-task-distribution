from app.core.config import settings
from app.models import Role, User, UserCreate
from app.services import user as user_service
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Session, create_engine, select, text

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

import pandas as pd
from sqlalchemy import create_engine


def csv_to_db_pandas(csv_file, engine, table_name):
    # Чтение CSV
    df = pd.read_csv(
        csv_file,
        sep=";",
        encoding="utf-8",
        header=0,
    )

    # Конвертируем строку JSON в Python объект
    import json

    df["route"] = df["route"].apply(json.loads)

    # Запись в БД с указанием типа JSONB
    dtype = {"route": JSONB}
    df.to_sql(table_name, engine, if_exists="replace", index=False, dtype=dtype)
    print(f"Загружено {len(df)} строк в таблицу {table_name}")


def init_db(session: Session) -> None:
    from sqlmodel import SQLModel

    SQLModel.metadata.create_all(engine)

    users = session.exec(select(User).limit(2)).all()
    if not users:
        with open("/app/backend/app/db/db.sql", "r", encoding="utf-8") as file:
            sql_script = file.read()

        session.exec(text(sql_script))
        session.commit()

        csv_to_db_pandas(
            "/app/backend/app/db/location_edge.csv", engine, "location_edge"
        )

        session.commit()
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
