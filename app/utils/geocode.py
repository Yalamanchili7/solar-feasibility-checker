import os
import json
import hashlib
from pathlib import Path
import requests

CACHE_DIR = Path("app/data/geocode_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def geocode_address(address: str):
    """Geocode address string to (lat, lon) with caching for resilience."""
    key = hashlib.md5(address.lower().encode()).hexdigest()
    cache_path = CACHE_DIR / f"{key}.json"

    # ✅ Return cached result if available
    if cache_path.exists():
        try:
            with open(cache_path, "r") as f:
                data = json.load(f)
                return float(data["lat"]), float(data["lon"])
        except Exception:
            pass

    base_url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json", "limit": 1}
    headers = {"User-Agent": "solar-feasibility-checker"}

    try:
        resp = requests.get(base_url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data:
            lat, lon = float(data[0]["lat"]), float(data[0]["lon"])

            # ✅ Save to cache
            with open(cache_path, "w") as f:
                json.dump({"lat": lat, "lon": lon}, f)

            return lat, lon
    except Exception as e:
        print(f"⚠️ Geocoding failed for {address}: {e}")

    # Default fallback to Phoenix, AZ (safe default)
    return 33.4484, -112.0740
