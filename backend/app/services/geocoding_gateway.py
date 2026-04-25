from app.geocoding import get_lat_lon


class GeocodingUnavailableError(Exception):
    pass


class AddressNotFoundError(Exception):
    pass


def geocode_address(address: str) -> tuple[float, float]:
    try:
        coordinates = get_lat_lon([address])
    except Exception as exc:  # noqa: BLE001
        raise GeocodingUnavailableError("Geocoding service unavailable") from exc

    if not coordinates:
        raise GeocodingUnavailableError("Geocoding service unavailable")

    lat, lon = coordinates[0]
    if lat is None or lon is None:
        raise AddressNotFoundError("Address not found")
    return lat, lon
