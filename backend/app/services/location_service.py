from fastapi import HTTPException
from sqlmodel import Session

from app.models import Location, LocationCreate, LocationUpdate
from app.repositories import location as location_repository
from app.services.geocoding_gateway import (
    AddressNotFoundError,
    GeocodingUnavailableError,
    geocode_address,
)


def create_location(*, session: Session, location_in: LocationCreate) -> Location:
    lat, lon = _safe_geocode(location_in.address)
    payload = location_in.model_dump()
    payload["lat"] = lat
    payload["lon"] = lon
    location = Location.model_validate(payload)
    return location_repository.save(session=session, location=location)


def update_location(*, session: Session, location: Location, location_in: LocationUpdate) -> Location:
    update_dict = location_in.model_dump(exclude_unset=True)
    if "address" in update_dict:
        lat, lon = _safe_geocode(update_dict["address"])
        update_dict["lat"] = lat
        update_dict["lon"] = lon
    location.sqlmodel_update(update_dict)
    return location_repository.save(session=session, location=location)


def _safe_geocode(address: str) -> tuple[float, float]:
    try:
        return geocode_address(address)
    except GeocodingUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except AddressNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
