import json
import re

# Замените эти имена на свои
input_file = "coordinates.txt"
output_file = "linestrings.txt"


def parse_and_convert(line):
    """Преобразует строку в LINESTRING"""
    line = line.strip().strip('"')

    # Парсим JSON
    try:
        coords = json.loads(line)
    except:
        # Если не JSON, парсим числа
        numbers = re.findall(r"-?\d+\.?\d*", line)
        coords = []
        for i in range(0, len(numbers), 2):
            if i + 1 < len(numbers):
                coords.append([float(numbers[i]), float(numbers[i + 1])])

    # Создаем LINESTRING
    if len(coords) >= 2:
        points = [f"{lon} {lat}" for lon, lat in coords]
        return f"LINESTRING({', '.join(points)})"
    return None


# Читаем и преобразуем
with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

with open(output_file, "w", encoding="utf-8") as f:
    for line in lines:
        if line.strip():
            result = parse_and_convert(line)
            if result:
                f.write(result + "\n")

print(f"Преобразовано {len(lines)} строк в {output_file}")
