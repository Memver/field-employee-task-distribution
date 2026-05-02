from app.distance_matrix import get_distance_matrix
from app.models import Location


def get_distance_and_time_matrix(
    locations: list[Location],
) -> tuple[list[list[float]], list[list[float]]]:
    """
    Возвращает матрицы расстояний и времени для списка локаций.

    Returns:
        tuple[list[list[float]], list[list[float]]]:
            - distance_matrix (метры)
            - time_matrix (секунды)
    """
    if not locations:
        return [], []

    coordinates = [(location.lon, location.lat) for location in locations]
    durations, distances = get_distance_matrix(coordinates)

    return distances.tolist(), durations.tolist()
