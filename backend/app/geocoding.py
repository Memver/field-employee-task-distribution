import time
from typing import List, Tuple
import logging

import requests

logger = logging.getLogger(__name__)

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
            else:
                logger.info("Address not found during geocoding: %s", address)
                results.append((None, None))

            time.sleep(1)

        except requests.RequestException:
            logger.exception("Geocoding request failed for address '%s'", address)
            results.append((None, None))
        except (ValueError, KeyError):
            logger.exception("Failed to parse geocoding response for '%s'", address)
            results.append((None, None))

    return results
