# src/utils/geo.py

import re
import requests
import os

PHOTON_URL = "https://photon.komoot.io/api/"
HEADERS = {"User-Agent": "solar-feasibility/0.1"}

def validate_address_format(address: str) -> bool:
    """
    Check if the address roughly follows a 'Street, City, ST' pattern.
    Example of valid inputs:
        "123 Solar Way, Phoenix, AZ"
        "456 Elm Street, Tempe, AZ"
    """
    # Expect at least one comma and a state abbreviation (2 letters)
    pattern = r"^.+,\s*[\w\s]+,\s*[A-Z]{2}$"
    return bool(re.match(pattern, address.strip(), re.IGNORECASE))


def parse_jurisdiction_from_address(address: str):
    """
    Extract (city, state, country) from a full address string.
    Falls back gracefully if only partial info is given.
    """
    address = address.strip()

    if not validate_address_format(address):
        raise ValueError(
            f"Invalid address format: {address}. "
            "Please enter in the format '123 Main St, City, ST' (e.g., '123 Solar Way, Phoenix, AZ')."
        )

    parts = [p.strip() for p in address.split(",") if p.strip()]
    if len(parts) < 3:
        raise ValueError(f"Invalid address format: {address}")

    city = parts[-2]
    state = parts[-1]
    return city, state, "USA"


def geocode(address: str):
    """Optional geocoding stub using the Photon API."""
    if os.getenv("GEOCODER", "none") != "photon":
        return None
    try:
        r = requests.get(PHOTON_URL, params={"q": address, "limit": 1}, timeout=8)
        r.raise_for_status()
        js = r.json()
        if js.get("features"):
            return js["features"][0]
    except Exception:
        return None
    return None


def jurisdiction_for_address(address: str) -> str:
    """
    Use Photon if available; otherwise fall back to parsing.
    """
    geo = geocode(address)
    if geo is None:
        city, state, _ = parse_jurisdiction_from_address(address)
        return f"{city}, {state}"
    props = geo.get("properties") or {}
    city = props.get("city") or props.get("name") or ""
    state = props.get("state") or props.get("statecode") or ""
    return ", ".join([s for s in [city, state] if s])
