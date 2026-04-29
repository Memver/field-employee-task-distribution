from typing import List, Tuple

import numpy as np
from app.core.config import settings
from routingpy import OSRM


def get_distance_matrix(
    locations: List[Tuple[float, float]],
    profile: str = "driving",
    host: str | None = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Вычисляет матрицы времени и расстояний через OSRM.

    Args:
        locations: Список координат (долгота, широта).
        profile: Профиль маршрута ('driving', 'walking', 'cycling').
        host: URL сервера OSRM (публичный или локальный).

    Returns:
        Tuple[np.ndarray, np.ndarray]:
            - Первая матрица: время в секундах (N x N)
            - Вторая матрица: расстояние в метрах (N x N)
    """
    client = OSRM(base_url=host or settings.OSRM_BASE_URL)

    matrix = client.matrix(locations=locations, profile=profile)

    durations = np.array(matrix.durations)
    distances = np.array(matrix.distances)

    return durations, distances


# Пример использования
if __name__ == "__main__":
    points = [
        (13.388860, 52.517037),  # Берлин, Бранденбургские ворота
        (13.397634, 52.529407),  # Берлин, Центральный вокзал
        (13.428555, 52.507220),  # Берлин, Ист-Сайд-Галерея
    ]

    durations, distances = get_distance_matrix(points)

    print("Матрица времени (секунды):")
    print(durations)

    print("\nМатрица времени (минуты):")
    print(np.round(durations / 60, 1))

    print("\nМатрица расстояний (метры):")
    print(distances)

    print("\nМатрица расстояний (километры):")
    print(np.round(distances / 1000, 1))
