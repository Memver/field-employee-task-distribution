import json
from typing import Dict, List, Optional, Tuple

import requests


def get_route_osm(
    start_point: Tuple[float, float],  # (широта, долгота)
    end_point: Tuple[float, float],  # (широта, долгота)
) -> Optional[Dict]:
    """
    Получение маршрута через OSRM API (OpenStreetMap)
    Не требует API ключа
    """

    mode: str = "driving"  # driving, walking, bicycling

    # OSRM API endpoint
    base_url = "http://router.project-osrm.org/route/v1"

    # Преобразование режима передвижения
    profile = {"driving": "driving", "walking": "walking", "bicycling": "cycling"}.get(
        mode, "driving"
    )

    # Формируем координаты в формате "долгота,широта;долгота,широта"
    coordinates = f"{start_point[1]},{start_point[0]};{end_point[1]},{end_point[0]}"

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

        print("Маршрут не найден")
        return None

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе: {e}")
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


# Пример использования OSM
if __name__ == "__main__":
    # Координаты в формате (широта, долгота)
    point_a = (55.751244, 37.617633)  # Красная площадь, Москва
    point_b = (55.703885, 37.530553)  # МГУ, Москва

    route = get_route_osm(point_a, point_b)

    if route:
        parsed = parse_osm_route(route)
        print(f"Расстояние: {parsed['distance_km']:.2f} км")
        print(f"Время в пути: {parsed['duration_minutes']:.0f} минут")
        print(f"\nВсего шагов: {len(parsed['steps'])}")

        # Выводим  шаги
        for i, step in enumerate(parsed["steps"], 1):
            print(f"{i}. {step['location']} ({step['distance']:.0f} м)")
