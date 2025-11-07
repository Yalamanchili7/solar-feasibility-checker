import json
import pandas as pd
from pathlib import Path

# Base data directory
DATA = Path(__file__).resolve().parent.parent / "data"

def read_json(filename: str):
    """Read a JSON file from the data directory."""
    file_path = DATA / filename
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_json(path: Path, data):
    """Write data (dict) to a JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def read_csv(filename: str):
    """Read a CSV file from the data directory using pandas."""
    file_path = DATA / filename
    return pd.read_csv(file_path)
 