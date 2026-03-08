import json
import time

import pandas as pd
import requests


def get_route_coordinates(from_lat, from_lon, to_lat, to_lon):
    """Получает координаты маршрута"""
    url = f"http://router.project-osrm.org/route/v1/driving/{from_lon},{from_lat};{to_lon},{to_lat}"
    params = {"overview": "full", "geometries": "geojson"}

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data["routes"]:
                return data["routes"][0]["geometry"]["coordinates"]
    except:
        pass
    return []


# Читаем входной файл
df = pd.read_csv("input_routes.csv")
print(f"Загружено {len(df)} маршрутов")

# Обрабатываем и сохраняем только координаты
results = []
total = len(df)

for i, row in df.iterrows():
    print(f"Обработка {i+1}/{total}...")

    coords = get_route_coordinates(
        row["from_lat"], row["from_lon"], row["to_lat"], row["to_lon"]
    )

    # Сохраняем только координаты как JSON-строку
    results.append({"coordinates": json.dumps(coords, ensure_ascii=False)})

    time.sleep(0.1)  # задержка

# Создаем DataFrame с одной колонкой и сохраняем
result_df = pd.DataFrame(results)
result_df.to_csv("routes_coordinates.csv", index=False, encoding="utf-8")

print(f"\nГотово! Файл сохранен как 'routes_coordinates.csv'")
print(f"Всего строк: {len(result_df)}")
