# Project Progress

Last updated: 2026-10-06

## Status by phase

| Phase | Description | Status |
|---|---|---|
| 1 | Data source research (OpenAQ + Open-Meteo) | Done |
| 2 | Python ingestion (OpenAQ + Open-Meteo clients) | In progress |
| 3 | Data lake (Parquet, date partitioning) | Not started |
| 4 | Data warehouse (Postgres) | Not started |
| 5 | dbt transformations | Scaffolding only |
| 6 | Airflow orchestration | Scaffolding only |
| 7 | Streamlit dashboard | Scaffolding only |
| 8 | Docker / reproducibility | In progress |

## Completed

- `research/check_openaq.py` — validated OpenAQ coverage for Hanoi / HCMC (PM2.5, PM1.0), hourly probes work with `OPENAQ_API_KEY`.
- `research/check_weather.py` — validated Open-Meteo archive API for both cities, hourly variables complete for last 30 days. No API key required.
- `ingestion/locations.yml` — location config skeleton (IDs/coords still TODO after research).
- `requirements.txt` — verified: `openmeteo-requests`, `pandas`, `requests-cache`, `retry-requests` + warehouse/dashboard deps all install and the Open-Meteo sample script runs against the live API.
- `.env.example` / `.env` — `OPENAQ_API_KEY` plus Postgres/Airflow/dashboard settings.
- `Dockerfile` — Python 3.11 slim image for ingestion, dbt, dashboard.
- `airflow/Dockerfile` — official Airflow 2.9.3 image + project requirements.
- `docker-compose.yml` — warehouse DB, Airflow DB, Airflow (init/webserver/scheduler), dbt, dashboard; `ingestion`/`dbt` behind `--profile tools`.

## Next steps

1. Fill in OpenAQ `location_id` / coordinates / sensors in `ingestion/locations.yml`.
2. Implement `ingestion/openaq/client.py`, `locations.py`, `measurements.py` (X-API-Key header, retries, 401/429 handling).
3. Implement `ingestion/weather/open_meteo.py` (archive + forecast, hourly, timezone Asia/Ho_Chi_Minh).
4. Write raw responses to `lake/raw/{air_quality,weather}/year=YYYY/month=MM/day=DD/` as Parquet.
5. Create `warehouse/init/init.sql` (raw tables) and load Parquet → Postgres.
6. Fill dbt models (`stg_*`, `int_*`, `fact_*`, `mart_*`) + schema tests.
7. Build the Airflow DAG: discover_locations → fetch → validate → lake → warehouse → dbt_run → dbt_test.
8. Build Streamlit pages querying the marts (avg PM2.5 by city, PM2.5 over time, weather vs PM2.5).
9. README quickstart: `cp .env.example .env && docker compose up`.

## Run commands

```bash
cp .env.example .env          # add your OpenAQ key
docker compose up -d          # warehouse + airflow + dashboard
docker compose ps             # check health
docker compose --profile tools run --rm dbt dbt build
docker compose --profile tools run --rm ingestion python -m ingestion.weather.open_meteo
```

Airflow UI: http://localhost:8080 (admin/admin by default)
Dashboard: http://localhost:8501
