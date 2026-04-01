from typing import List, Tuple, Union
import numpy as np
from routingpy import OSRM
from routingpy.routers import options

def get_distance_matrix_routingpy(
    locations: List[Tuple[float, float]],
    profile: str = "driving",
    host: str = "http://router.project-osrm.org",
    cost_type: str = "duration"
) -> np.ndarray:
    """
    Вычисляет матрицу расстояний/времени через OSRM используя routingpy.

    Args:
        locations: Список координат (долгота, широта).
        profile: Профиль маршрута ('driving', 'walking', 'cycling').
        host: URL сервера OSRM (публичный или локальный).
        cost_type: Тип стоимости ('duration' - секунды, 'distance' - метры).

    Returns:
        numpy.ndarray: Матрица размера NxN.
    """
    # Инициализируем клиент OSRM
    client = OSRM(base_url=host)
    
    # Выполняем запрос к матричному сервису
    # locations - это список [lon, lat]
    matrix = client.matrix(
        locations=locations,
        profile=profile
    )
    
    # Получаем нужную матрицу
    if cost_type == "duration":
        result = np.array(matrix.durations)
    elif cost_type == "distance":
        result = np.array(matrix.distances)
    else:
        raise ValueError("cost_type должен быть 'duration' или 'distance'")
    
    return result

# Пример использования
if __name__ == "__main__":
    # Точки в формате (Долгота, Широта)
    points = [
        (13.388860, 52.517037),  # Berlin Brandenburg Gate
        (13.397634, 52.529407),  # Berlin Central Station
        (13.428555, 52.507220)   # Berlin East Side Gallery
    ]
    
    # Используем публичный сервер OSRM
    matrix = get_distance_matrix_routingpy(points, cost_type="duration")
    print("Матрица времени (секунды):")
    print(matrix)
    
    # Округлим до минут для удобства
    print("\nМатрица времени (минуты):")
    print(np.round(matrix / 60, 1))
