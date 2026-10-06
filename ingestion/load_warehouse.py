"""Load data from Parquet files in the data lake into PostgreSQL warehouse."""

import os
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

from ingestion.config import LAKE_DIR, get_warehouse_config


def _get_conn():
    cfg = get_warehouse_config()
    return psycopg2.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        dbname=cfg["database"],
    )


def load_air_quality_to_warehouse() -> int:
    base = LAKE_DIR / "raw" / "air_quality"
    if not base.exists():
        return 0
    files = sorted(base.rglob("data.parquet"))
    if not files:
        return 0
    df = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
    if df.empty:
        return 0
    df = df.drop_duplicates(subset=["sensor_id", "parameter", "timestamp_utc"])
    records = [
        (
            r.get("location_id"), r.get("location_name"), r.get("city"),
            int(r["sensor_id"]), r["parameter"], float(r["value"]) if pd.notna(r["value"]) else None,
            r.get("unit"), r["timestamp_utc"].to_pydatetime(),
            r.get("latitude"), r.get("longitude"), "openaq",
        )
        for _, r in df.iterrows()
    ]
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            execute_values(
                cur,
                """INSERT INTO raw.raw_air_quality
                   (location_id, location_name, city, sensor_id, parameter, value, unit,
                    timestamp_utc, latitude, longitude, source)
                   VALUES %s ON CONFLICT DO NOTHING""",
                records,
                page_size=1000,
            )
        conn.commit()
    finally:
        conn.close()
    return len(records)


def load_weather_to_warehouse() -> int:
    base = LAKE_DIR / "raw" / "weather"
    if not base.exists():
        return 0
    files = sorted(base.rglob("data.parquet"))
    if not files:
        return 0
    df = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
    if df.empty:
        return 0
    df = df.drop_duplicates(subset=["city", "timestamp"])
    records = []
    for _, r in df.iterrows():
        ts = r["timestamp"]
        if hasattr(ts, "to_pydatetime"):
            ts = ts.to_pydatetime()
        records.append((
            r["city"], r.get("latitude"), r.get("longitude"), ts,
            float(r["temperature"]) if pd.notna(r.get("temperature")) else None,
            float(r["relative_humidity"]) if pd.notna(r.get("relative_humidity")) else None,
            float(r["precipitation"]) if pd.notna(r.get("precipitation")) else None,
            float(r["wind_speed"]) if pd.notna(r.get("wind_speed")) else None,
            float(r["wind_direction"]) if pd.notna(r.get("wind_direction")) else None,
            float(r["surface_pressure"]) if pd.notna(r.get("surface_pressure")) else None,
            "open_meteo",
        ))
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            execute_values(
                cur,
                """INSERT INTO raw.raw_weather
                   (city, latitude, longitude, timestamp, temperature, relative_humidity,
                    precipitation, wind_speed, wind_direction, surface_pressure, source)
                   VALUES %s ON CONFLICT DO NOTHING""",
                records,
                page_size=1000,
            )
        conn.commit()
    finally:
        conn.close()
    return len(records)
