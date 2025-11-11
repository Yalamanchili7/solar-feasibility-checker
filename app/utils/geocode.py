# app/utils/geocode.py

import requests
from urllib.parse import urlencode

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

def geocode_address(address: str):
    """
    Geocode an address to lat/lon using OpenStreetMap Nominatim.
    This is a simple MVP – in production you'd handle rate limits, user agent, etc.
    """
    params = {
        "q": address,
        "format": "json",
        "limit": 1,
    }
    headers = {
        "User-Agent": "solar-feasibility-checker/1.0 (contact: example@example.com)"
    }

    try:
        resp = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            return None, None
        lat = float(data[0]["lat"])
        lon = float(data[0]["lon"])
        return lat, lon
    except Exception as e:
        print(f"Geocoding error for '{address}': {e}")
        return None, None
