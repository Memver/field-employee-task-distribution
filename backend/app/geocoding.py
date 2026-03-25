import time
import requests
from typing import List, Tuple, Optional

def get_lat_lon(addresses: List[str]) -> List[Tuple[float, float]]:
    results = []
    
    base_url = "https://nominatim.openstreetmap.org/search"
    
    headers = {
        'User-Agent': 'GeocodingApp/1.0 ka_ba@bk.ru'
    }
    
    for address in addresses:
        try:
            params = {
                'q': address,
                'format': 'json',
                'limit': 1, 
                'addressdetails': 0
            }
            
            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if data and len(data) > 0:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                results.append((lat, lon))
                print(f"Найден: {address} ({lat:.6f}, {lon:.6f})")
            else:
                print(f"Не найден: {address}")
                results.append((None, None))
            
            # Задержка для соблюдения политики использования API
            # Nominatim требует не более 1 запроса в секунду
            time.sleep(1)
            
        except requests.RequestException as e:
            print(f"Ошибка при запросе для '{address}': {e}")
            results.append((None, None))
        except (ValueError, KeyError) as e:
            print(f"Ошибка обработки данных для '{address}': {e}")
            results.append((None, None))
    
    return results


if __name__ == "__main__":
    addresses = [
        "Red Square, Moscow, Russia",
        "Eiffel Tower, Paris, France",
        "Statue of Liberty, New York, USA",
        "Несуществующий адрес, Город, Страна"
    ]
    
    coordinates = get_lat_lon(addresses)
    
    for addr, coord in zip(addresses, coordinates):
        lat, lon = coord
        if lat is not None and lon is not None:
            print(f"{addr}: ({lat:.6f}, {lon:.6f})")
        else:
            print(f"{addr}: Не найден")
