"""Dashboard warehouse connection utility."""

import os

import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor


def get_connection():
    return psycopg2.connect(
        host=os.getenv("WAREHOUSE_HOST", "localhost"),
        port=int(os.getenv("WAREHOUSE_PORT", "5432")),
        user=os.getenv("POSTGRES_USER", "vt_analytics"),
        password=os.getenv("POSTGRES_PASSWORD", "change_me"),
        dbname=os.getenv("POSTGRES_DB", "vietnam_air_quality"),
    )


def query_to_df(sql: str) -> pd.DataFrame:
    conn = get_connection()
    try:
        return pd.read_sql(sql, conn)
    finally:
        conn.close()


def get_city_daily() -> pd.DataFrame:
    return query_to_df("SELECT * FROM analytics_analytics.mart_city_daily ORDER BY date DESC")


def get_pollution_weather() -> pd.DataFrame:
    return query_to_df("""
        SELECT * FROM analytics_analytics.mart_pollution_weather
        ORDER BY timestamp_utc DESC
        LIMIT 10000
    """)


def get_air_quality_hourly() -> pd.DataFrame:
    return query_to_df("""
        SELECT * FROM analytics_analytics.fact_air_quality_hourly
        ORDER BY timestamp_utc DESC
        LIMIT 10000
    """)


def get_weather_hourly() -> pd.DataFrame:
    return query_to_df("""
        SELECT * FROM analytics_analytics.fact_weather_hourly
        ORDER BY timestamp DESC
        LIMIT 10000
    """)
