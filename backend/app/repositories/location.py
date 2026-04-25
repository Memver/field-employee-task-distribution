from sqlmodel import Session, select

from app.models import Location


def get_by_id(*, session: Session, location_id: int) -> Location | None:
    return session.get(Location, location_id)


def list_all(*, session: Session) -> list[Location]:
    return session.exec(select(Location)).all()


def save(*, session: Session, location: Location) -> Location:
    session.add(location)
    session.commit()
    session.refresh(location)
    return location
