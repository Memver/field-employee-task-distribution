from typing import Dict, List, Optional, Tuple

import requests
import logging

logger = logging.getLogger(__name__)


def get_route_osm(
    points: List[Tuple[float, float]],  # каждая точка: (широта, долгота)
) -> Optional[Dict]:
    """
    Получение маршрута через OSRM API (OpenStreetMap) по цепочке точек (waypoints по порядку).
    Не требует API ключа.

    points: от 2 до 25 точек включительно.
    """
    n = len(points)
    if n < 2:
        raise ValueError("points must contain at least 2 coordinates")
    if n > 25:
        raise ValueError("points must contain at most 25 coordinates")

    mode: str = "driving"  # driving, walking, bicycling

    # OSRM API endpoint
    base_url = "http://router.project-osrm.org/route/v1"

    # Преобразование режима передвижения
    profile = {"driving": "driving", "walking": "walking", "bicycling": "cycling"}.get(
        mode, "driving"
    )

    # Формируем координаты в формате "долгота,широта;долгота,широта;..."
    coordinates = ";".join(f"{lon},{lat}" for lat, lon in points)

    # URL для запроса
    url = f"{base_url}/{profile}/{coordinates}"

    # Параметры запроса
    params = {
        "overview": "full",  # Полный обзор маршрута
        "geometries": "geojson",  # Формат геометрии
        "steps": "true",  # Включить шаги маршрута
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        if data.get("code") == "Ok" and data.get("routes"):
            return data

        logger.info("OSRM route was not found for provided points")
        return None

    except requests.exceptions.RequestException:
        logger.exception("OSRM request failed")
        return None


def parse_osm_route(route_data: Dict) -> Dict:
    """
    Парсинг данных маршрута из OSRM
    """
    if not route_data or "routes" not in route_data:
        return {}

    route = route_data["routes"][0]

    result = {
        "distance_meters": route.get("distance", 0),
        "distance_km": route.get("distance", 0) / 1000,
        "duration_seconds": route.get("duration", 0),
        "duration_minutes": route.get("duration", 0) / 60,
        "steps": [],
    }

    # Извлекаем шаги маршрута
    if "legs" in route:
        for leg in route["legs"]:
            for step in leg.get("steps", []):
                if "maneuver" in step and "location" in step["maneuver"]:
                    step_info = {
                        "distance": step.get("distance", 0),
                        "duration": step.get("duration", 0),
                        "location": step["maneuver"]["location"],
                        "way_points": step.get("way_points", []),
                    }
                    result["steps"].append(step_info)

    return result


def edge_fields_from_osm_response(
    route_data: Dict,
) -> Optional[Tuple[float, int, List[List[float]]]]:
    """
    Из ответа get_route_osm: километры, время в секундах (int), линия [[lon, lat], ...].
    """
    if not route_data or "routes" not in route_data:
        return None
    route = route_data["routes"][0]
    geom = route.get("geometry") or {}
    coords = geom.get("coordinates")
    if not coords:
        return None
    meters = float(route.get("distance", 0))
    duration = float(route.get("duration", 0))
    distance_km = meters / 1000.0
    time_seconds = int(round(duration))
    route_points: List[List[float]] = [[float(c[0]), float(c[1])] for c in coords]
    return (distance_km, time_seconds, route_points)


