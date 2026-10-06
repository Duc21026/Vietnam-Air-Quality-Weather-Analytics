"""Project configuration: env vars + locations.yml."""

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
LAKE_DIR = BASE_DIR / "lake"
LOCATIONS_FILE = BASE_DIR / "ingestion" / "locations.yml"

load_dotenv(BASE_DIR / ".env")


def get_openaq_api_key() -> str:
    key = os.getenv("OPENAQ_API_KEY", "").strip()
    if not key:
        raise RuntimeError("OPENAQ_API_KEY not set")
    return key


def get_warehouse_config() -> dict:
    return {
        "host": os.getenv("WAREHOUSE_HOST", "localhost"),
        "port": int(os.getenv("WAREHOUSE_PORT", "5432")),
        "user": os.getenv("POSTGRES_USER", "vt_analytics"),
        "password": os.getenv("POSTGRES_PASSWORD", "change_me"),
        "database": os.getenv("POSTGRES_DB", "vietnam_air_quality"),
    }


def load_locations() -> list[dict]:
    with open(LOCATIONS_FILE) as f:
        data = yaml.safe_load(f)
    cities = []
    for city_entry in data.get("cities", []):
        for loc in city_entry.get("locations", []):
            cities.append({
                "city": city_entry["city"],
                "country": city_entry.get("country", "VN"),
                "location_id": loc["location_id"],
                "location_name": loc["location_name"],
                "latitude": loc["coordinates"]["latitude"],
                "longitude": loc["coordinates"]["longitude"],
                "sensors": loc.get("sensors", []),
                "parameters": loc.get("parameters", []),
            })
    return cities


def get_weather_variables() -> list[str]:
    with open(LOCATIONS_FILE) as f:
        data = yaml.safe_load(f)
    return data.get("weather_variables", [
        "temperature", "relative_humidity", "precipitation",
        "wind_speed", "surface_pressure",
    ])
