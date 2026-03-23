import time
import requests
from typing import List, Tuple, Optional

def get_lat_lon(addresses: List[str]) -> List[Tuple[float, float]]:
    """
    Преобразует список адресов в координаты широты и долготы.
    
    Args:
        addresses: Список адресов в виде строк
        
    Returns:
        Список кортежей (широта, долгота) для каждого адреса.
        Если адрес не найден, возвращает (None, None)
        
    Raises:
        requests.RequestException: При проблемах с сетью
    """
    results = []
    
    # Базовый URL для Nominatim API
    base_url = "https://nominatim.openstreetmap.org/search"
    
    # Заголовки для соблюдения правил использования
    headers = {
        'User-Agent': 'GeocodingApp/1.0 ka_ba@bk.ru'
    }
    
    for address in addresses:
        try:
            # Параметры запроса
            params = {
                'q': address,
                'format': 'json',
                'limit': 1,  # Берем только первый результат
                'addressdetails': 0
            }
            
            # Выполняем запрос
            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if data and len(data) > 0:
                # Извлекаем координаты
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                results.append((lat, lon))
                print(f"✓ Найден: {address} -> ({lat:.6f}, {lon:.6f})")
            else:
                print(f"✗ Не найден: {address}")
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
