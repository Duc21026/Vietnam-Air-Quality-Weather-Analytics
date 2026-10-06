"""Write data to the local data lake as Parquet with date partitioning."""

from pathlib import Path

import pandas as pd

from ingestion.config import LAKE_DIR


def write_parquet_partitioned(
    df: pd.DataFrame,
    dataset: str,
    layer: str,
    date_col: str = "timestamp_utc",
) -> Path:
    if df.empty:
        return None
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], utc=True)
    year = df[date_col].dt.year.astype(str)
    month = df[date_col].dt.month.astype(str).str.zfill(2)
    day = df[date_col].dt.day.astype(str).str.zfill(2)
    base = LAKE_DIR / layer / dataset
    written = []
    for (y, m, d), group in df.groupby([year, month, day]):
        dir_path = base / f"year={y}" / f"month={m}" / f"day={d}"
        dir_path.mkdir(parents=True, exist_ok=True)
        file_path = dir_path / "data.parquet"
        group.to_parquet(file_path, index=False)
        written.append(file_path)
    return written[0].parent if written else None


def write_air_quality_raw(df: pd.DataFrame) -> Path:
    return write_parquet_partitioned(df, "air_quality", "raw")


def write_weather_raw(df: pd.DataFrame) -> Path:
    return write_parquet_partitioned(df, "weather", "raw", date_col="timestamp")
