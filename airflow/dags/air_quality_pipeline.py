"""Vietnam Air Quality & Weather Analytics — end-to-end Airflow DAG.

Pipeline:
  check_api
    ├── extract_air_quality → validate_air_quality → save_air_quality
    └── extract_weather     → validate_weather     → save_weather
          ↓ (both save tasks complete)
    load_to_warehouse → dbt_run → dbt_test
"""

import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

BASE_DIR = Path(__file__).resolve().parent.parent
CODE_DIR = BASE_DIR / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from ingestion.config import get_openaq_api_key, load_locations, get_weather_variables
from ingestion.openaq.measurements import fetch_measurements
from ingestion.weather.open_meteo import fetch_last_n_days
from ingestion.lake import write_air_quality_raw, write_weather_raw
from ingestion.load_warehouse import load_air_quality_to_warehouse, load_weather_to_warehouse

LOOKBACK_DAYS = 7


def _check_api(**ctx):
    key = get_openaq_api_key()
    assert len(key) > 10, "API key too short"
    locations = load_locations()
    assert len(locations) >= 2, f"expected >=2 locations, got {len(locations)}"
    print(f"API key OK, {len(locations)} locations configured")
    return True


def _extract_air_quality(**ctx):
    api_key = get_openaq_api_key()
    locations = load_locations()
    dt_to = datetime.now(timezone.utc)
    dt_from = dt_to - timedelta(days=LOOKBACK_DAYS)
    all_frames = []
    for loc in locations:
        for sensor in loc.get("sensors", []):
            sid = sensor["sensor_id"]
            param = sensor["parameter"]
            print(f"Fetching {loc['city']} sensor={sid} param={param}")
            df = fetch_measurements(sid, api_key, dt_from, dt_to)
            if not df.empty:
                df["location_id"] = loc["location_id"]
                df["location_name"] = loc["location_name"]
                df["city"] = loc["city"]
                df["latitude"] = loc["latitude"]
                df["longitude"] = loc["longitude"]
                all_frames.append(df)
    if not all_frames:
        raise RuntimeError("No air quality data fetched")
    import pandas as pd
    combined = pd.concat(all_frames, ignore_index=True)
    combined = combined.drop_duplicates(subset=["sensor_id", "parameter", "timestamp_utc"])
    print(f"Fetched {len(combined)} air quality rows")
    return combined.to_json()


def _extract_weather(**ctx):
    locations = load_locations()
    variables = get_weather_variables()
    cities = {}
    for loc in locations:
        cities[loc["city"]] = (loc["latitude"], loc["longitude"])
    all_frames = []
    import pandas as pd
    for city, (lat, lon) in cities.items():
        print(f"Fetching weather for {city} ({lat}, {lon})")
        df = fetch_last_n_days(lat, lon, LOOKBACK_DAYS, variables)
        if not df.empty:
            df["city"] = city
            all_frames.append(df)
    if not all_frames:
        raise RuntimeError("No weather data fetched")
    combined = pd.concat(all_frames, ignore_index=True)
    combined = combined.drop_duplicates(subset=["city", "timestamp"])
    print(f"Fetched {len(combined)} weather rows")
    return combined.to_json()


def _validate_air_quality(**ctx):
    import pandas as pd
    ti = ctx["ti"]
    json_str = ti.xcom_pull(task_ids="extract_air_quality")
    df = pd.read_json(json_str)
    assert not df.empty, "air quality data is empty"
    required = ["timestamp_utc", "sensor_id", "parameter", "value", "city"]
    for col in required:
        assert col in df.columns, f"missing column: {col}"
    assert df["timestamp_utc"].notna().all(), "null timestamps"
    assert df["value"].notna().all(), "null values"
    print(f"Validated {len(df)} air quality rows")
    return True


def _validate_weather(**ctx):
    import pandas as pd
    ti = ctx["ti"]
    json_str = ti.xcom_pull(task_ids="extract_weather")
    df = pd.read_json(json_str)
    assert not df.empty, "weather data is empty"
    required = ["timestamp", "city", "temperature"]
    for col in required:
        assert col in df.columns, f"missing column: {col}"
    print(f"Validated {len(df)} weather rows")
    return True


def _save_air_quality(**ctx):
    import pandas as pd
    ti = ctx["ti"]
    json_str = ti.xcom_pull(task_ids="extract_air_quality")
    df = pd.read_json(json_str)
    path = write_air_quality_raw(df)
    print(f"Saved air quality to {path}")
    return str(path)


def _save_weather(**ctx):
    import pandas as pd
    ti = ctx["ti"]
    json_str = ti.xcom_pull(task_ids="extract_weather")
    df = pd.read_json(json_str)
    path = write_weather_raw(df)
    print(f"Saved weather to {path}")
    return str(path)


def _load_to_warehouse(**ctx):
    aq_count = load_air_quality_to_warehouse()
    wx_count = load_weather_to_warehouse()
    print(f"Loaded {aq_count} AQ rows, {wx_count} weather rows to warehouse")
    return {"air_quality": aq_count, "weather": wx_count}


def _dbt_run(**ctx):
    import subprocess
    result = subprocess.run(
        ["dbt", "run", "--profiles-dir", "/opt/airflow/code/dbt/profiles",
         "--project-dir", "/opt/airflow/code/dbt/vietnam_air_quality"],
        capture_output=True, text=True,
    )
    print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
    if result.returncode != 0:
        print(result.stderr[-2000:])
        raise RuntimeError(f"dbt run failed: {result.returncode}")
    return True


def _dbt_test(**ctx):
    import subprocess
    result = subprocess.run(
        ["dbt", "test", "--profiles-dir", "/opt/airflow/code/dbt/profiles",
         "--project-dir", "/opt/airflow/code/dbt/vietnam_air_quality"],
        capture_output=True, text=True,
    )
    print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
    if result.returncode != 0:
        print(result.stderr[-2000:])
        raise RuntimeError(f"dbt test failed: {result.returncode}")
    return True


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="vietnam_air_quality_weather_dag",
    default_args=default_args,
    description="Vietnam Air Quality & Weather Analytics pipeline",
    schedule_interval="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["vietnam", "air_quality", "weather"],
) as dag:

    check_api = PythonOperator(
        task_id="check_api",
        python_callable=_check_api,
    )

    extract_air_quality = PythonOperator(
        task_id="extract_air_quality",
        python_callable=_extract_air_quality,
    )

    extract_weather = PythonOperator(
        task_id="extract_weather",
        python_callable=_extract_weather,
    )

    validate_air_quality = PythonOperator(
        task_id="validate_air_quality",
        python_callable=_validate_air_quality,
    )

    validate_weather = PythonOperator(
        task_id="validate_weather",
        python_callable=_validate_weather,
    )

    save_air_quality = PythonOperator(
        task_id="save_air_quality",
        python_callable=_save_air_quality,
    )

    save_weather = PythonOperator(
        task_id="save_weather",
        python_callable=_save_weather,
    )

    load_to_warehouse = PythonOperator(
        task_id="load_to_warehouse",
        python_callable=_load_to_warehouse,
    )

    dbt_run = PythonOperator(
        task_id="dbt_run",
        python_callable=_dbt_run,
    )

    dbt_test = PythonOperator(
        task_id="dbt_test",
        python_callable=_dbt_test,
    )

    check_api >> [extract_air_quality, extract_weather]
    extract_air_quality >> validate_air_quality >> save_air_quality
    extract_weather >> validate_weather >> save_weather
    [save_air_quality, save_weather] >> load_to_warehouse >> dbt_run >> dbt_test
