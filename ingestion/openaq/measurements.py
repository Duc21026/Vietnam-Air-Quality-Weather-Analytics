"""OpenAQ measurements: fetch and normalize hourly data."""

from datetime import datetime, timezone

import pandas as pd

from ingestion.openaq.client import fetch_sensor_hours


def fetch_measurements(
    sensor_id: int,
    api_key: str,
    datetime_from: datetime,
    datetime_to: datetime,
) -> pd.DataFrame:
    raw = fetch_sensor_hours(sensor_id, api_key, datetime_from, datetime_to)
    rows = []
    for r in raw:
        if r.get("value") is None:
            continue
        period = r.get("period") or {}
        dt_from = (period.get("datetimeFrom") or {}).get("utc")
        if not dt_from:
            continue
        param = r.get("parameter") or {}
        rows.append({
            "timestamp_utc": dt_from,
            "sensor_id": sensor_id,
            "parameter": param.get("name", ""),
            "value": r["value"],
            "unit": param.get("units", ""),
        })
    if not rows:
        return pd.DataFrame(columns=["timestamp_utc", "sensor_id", "parameter", "value", "unit"])
    df = pd.DataFrame(rows)
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], utc=True)
    return df
