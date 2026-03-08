from typing import Any

from app.api.deps import SessionDep
from app.models import Location, LocationPublic, LocationsPublic, Message
from fastapi import APIRouter
from sqlmodel import func, select

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get(
    "/",
    response_model=LocationsPublic,
)
def read_locations(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve locations.
    """

    count_statement = select(func.count()).select_from(Location)
    count = session.exec(count_statement).one()

    statement = select(Location).offset(skip).limit(limit)
    locations = session.exec(statement).all()

    return LocationsPublic(data=locations, count=count)


@router.get("/{location_id}", response_model=LocationPublic)
def read_location_by_id(location_id: int, session: SessionDep) -> Any:
    """
    Get a specific location by id.
    """
    location = session.get(Location, location_id)
    return location


@router.delete("/{location_id}")
def delete_location(session: SessionDep, location_id: int) -> Message:
    """
    Delete a location.
    """
    location = session.get(Location, location_id)
    # statement = delete(Item).where(col(Item.owner_id) == location_id)
    # session.exec(statement)
    session.delete(location)
    session.commit()
    return Message(message="Location deleted successfully")
