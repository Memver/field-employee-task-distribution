from app.path import edge_fields_from_osm_response, get_route_osm


def build_route(points: list[tuple[float, float]]) -> list[list[float]] | None:
    if len(points) < 2:
        return None
    route_data = get_route_osm(points)
    parsed_route = edge_fields_from_osm_response(route_data) if route_data else None
    if parsed_route is None:
        return None
    _distance_km, _time_seconds, route_points = parsed_route
    return route_points
