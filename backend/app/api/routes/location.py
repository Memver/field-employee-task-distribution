from typing import Any

from app.api.deps import EmployeeManagerUser, ManagerOrFieldEmployeeUser, SessionDep
from app.models import (
    Location,
    LocationCreate,
    LocationPublic,
    LocationsPublic,
    LocationUpdate,
    Message,
)
from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

router = APIRouter(prefix="/locations", tags=["locations"])


@router.post("/", response_model=LocationPublic)
def create_location(
    *, session: SessionDep, _em: EmployeeManagerUser, location_in: LocationCreate
) -> Any:
    """
    Create new location.
    """
    location = Location.model_validate(location_in)
    session.add(location)
    session.commit()
    session.refresh(location)
    return location


@router.get(
    "/",
    response_model=LocationsPublic,
)
def read_locations(
    session: SessionDep, _reader: ManagerOrFieldEmployeeUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve locations.
    """

    count_statement = select(func.count()).select_from(Location)
    count = session.exec(count_statement).one()

    statement = select(Location).offset(skip).limit(limit)
    locations = session.exec(statement).all()

    return LocationsPublic(data=locations, count=count)


@router.get("/{location_id}", response_model=LocationPublic)
def read_location_by_id(
    location_id: int, session: SessionDep, _reader: ManagerOrFieldEmployeeUser
) -> Any:
    """
    Get a specific location by id.
    """
    location = session.get(Location, location_id)
    return location


@router.put("/{id}", response_model=LocationPublic)
def update_location(
    *,
    session: SessionDep,
    _em: EmployeeManagerUser,
    id: int,
    location_in: LocationUpdate,
) -> Any:
    """
    Update an location.
    """
    location = session.get(Location, id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    update_dict = location_in.model_dump(exclude_unset=True)
    location.sqlmodel_update(update_dict)
    session.add(location)
    session.commit()
    session.refresh(location)
    return location


@router.delete("/{location_id}")
def delete_location(
    session: SessionDep, _em: EmployeeManagerUser, location_id: int
) -> Message:
    """
    Delete a location.
    """
    location = session.get(Location, location_id)
    # statement = delete(Item).where(col(Item.owner_id) == location_id)
    # session.exec(statement)
    session.delete(location)
    session.commit()
    return Message(message="Location deleted successfully")
