"""Open-Meteo weather data client."""

from datetime import date, timedelta

import pandas as pd
import requests

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
DEFAULT_TIMEOUT = 30

VAR_MAP = {
    "temperature": "temperature_2m",
    "relative_humidity": "relative_humidity_2m",
    "precipitation": "precipitation",
    "wind_speed": "wind_speed_10m",
    "wind_direction": "wind_direction_10m",
    "surface_pressure": "surface_pressure",
}


def fetch_weather(
    lat: float,
    lon: float,
    start_date: date,
    end_date: date,
    variables: list[str],
    timezone: str = "Asia/Ho_Chi_Minh",
) -> pd.DataFrame:
    hourly_vars = [VAR_MAP.get(v, v) for v in variables]
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "hourly": ",".join(hourly_vars),
        "timezone": timezone,
    }
    resp = requests.get(ARCHIVE_URL, params=params, timeout=DEFAULT_TIMEOUT)
    resp.raise_for_status()
    payload = resp.json()
    hourly = payload.get("hourly", {})
    times = hourly.get("time", [])
    if not times:
        return pd.DataFrame()
    df = pd.DataFrame({"timestamp": times})
    for var in variables:
        col = VAR_MAP.get(var, var)
        df[var] = hourly.get(col, [None] * len(times))
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["latitude"] = lat
    df["longitude"] = lon
    return df


def fetch_last_n_days(
    lat: float,
    lon: float,
    days: int,
    variables: list[str],
    timezone: str = "Asia/Ho_Chi_Minh",
) -> pd.DataFrame:
    end = date.today()
    start = end - timedelta(days=days)
    return fetch_weather(lat, lon, start, end, variables, timezone)
