from app.core.config import settings
from app.models import Role, User, UserCreate
from app.services import user as user_service
from sqlmodel import Session, create_engine, select, text

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

import pandas as pd
from sqlalchemy import create_engine


def csv_to_db_pandas(csv_file, engine, table_name):
    # Чтение CSV
    df = pd.read_csv(csv_file)

    # Запись в БД
    df.to_sql(table_name, engine, if_exists="replace", index=False)
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

        script = """-- Создаем новую колонку
    ALTER TABLE location_edge 
    ADD COLUMN IF NOT EXISTS route_geom geography(LINESTRING, 4326);
    
    -- Правильное преобразование: сначала декодируем hex в bytea, потом в геометрию
    UPDATE location_edge 
    SET route_geom = ST_GeomFromEWKB(decode(route, 'hex'))
    WHERE route IS NOT NULL 
      AND route != '' 
      AND route_geom IS NULL;
      ALTER TABLE location_edge DROP COLUMN IF EXISTS route;
            ALTER TABLE location_edge RENAME COLUMN route_geom TO route;"""
        session.exec(text(script))
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
