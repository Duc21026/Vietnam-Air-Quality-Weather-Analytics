# AGENTS.md

## What this repo is

Batch analytics pipeline for Hanoi and Ho Chi Minh City: OpenAQ + Open-Meteo -> Python ingestion -> Parquet lake -> Postgres raw tables -> dbt marts -> Streamlit dashboard. Docker Compose is the supported runtime; Airflow orchestrates the pipeline.

## Commands

- First run: `cp .env.example .env`, set `OPENAQ_API_KEY` (required; Open-Meteo needs no key), then `docker compose up -d`.
- Check stack: `docker compose ps`; logs: `docker compose logs -f airflow-scheduler`.
- Trigger pipeline: Airflow UI at `http://localhost:8080` (`admin`/`admin` defaults from `.env`), DAG `vietnam_air_quality_weather_dag`. CLI: `docker compose exec airflow-scheduler airflow dags trigger vietnam_air_quality_weather_dag`.
- Run dbt in container: `docker compose --profile tools run --rm dbt dbt build --project-dir /app/dbt/vietnam_air_quality --profiles-dir /app/dbt/profiles`.
- Single dbt model/test: add `--select <model>`; e.g. `... dbt run --select mart_city_pm25_comparison --project-dir ... --profiles-dir ...`.
- Local dbt (if installed): `dbt run --profiles-dir dbt/profiles --project-dir dbt/vietnam_air_quality` from repo root.
- Warehouse shell: `docker compose exec warehouse-db psql -U vt_analytics -d vietnam_air_quality`.
- Dashboard: `http://localhost:8501`.

## Key layout

- `ingestion/config.py` loads the root `.env` and `ingestion/locations.yml`. The YAML is the source of truth for cities, OpenAQ location/sensor IDs, coordinates, and weather variables.
- `airflow/dags/air_quality_pipeline.py` is the end-to-end DAG. In the Airflow image, DAGs are mounted at `/opt/airflow/dags` and project code at `/opt/airflow/code` (`PYTHONPATH=/opt/airflow/code`). Use those paths for new imports/subprocesses.
- `dbt/vietnam_air_quality/` is staging -> intermediate -> marts. `dbt/profiles/profiles.yml` supplies the Postgres target.
- `warehouse/init/init.sql` creates the `raw` tables. It runs only when the `warehouse_data` Docker volume is created for the first time.
- `dashboard/` is a Streamlit app rooted at `dashboard/app.py`; pages import `dashboard.utils.warehouse`, so run from repo root (`PYTHONPATH=.`) or `/app` in Docker.
- `lake/raw/{air_quality,weather}/year=.../month=.../day=.../data.parquet` is gitignored runtime data.

## Gotchas

- `.venv` is stale/broken: it resolves to Python 3.15 and `dbt`, `pytest`, and `pandas` are not importable. Use Docker (Python 3.11) or recreate the venv with Python 3.11.
- `README.md`, `PROGRESS.md`, `Makefile`, `docs/architecture.md`, and `docs/pipeline.md` are stubs/outdated; `tests/*.py` are empty. Do not treat them as truth or claim test coverage. `docs/data_dictionary.md` is the one reliable doc.
- dbt models land in schema `analytics_analytics` because `profiles.yml` sets `schema: analytics` and `dbt_project.yml` adds `+schema: analytics`. Dashboard queries hardcode `analytics_analytics.*`; change both together.
- `init.sql` will not re-run on an existing `warehouse_data` volume. Apply SQL manually or `docker compose down -v` (destroys warehouse data).
- Raw loaders re-read the entire Parquet lake on every run. `raw.raw_air_quality` has no unique constraint, so repeat loads accumulate duplicates; dbt de-duplicates in `int_hourly_air_quality` via `GROUP BY` + `MAX`. This is expected, not a new bug (also documented in `docs/data_dictionary.md`).
- Weather is fetched with `timezone=Asia/Ho_Chi_Minh` and stored as naive `timestamp`; OpenAQ timestamps are UTC. `int_air_quality_weather` joins them by exact equality, so timezone alignment is suspect -- verify before changing time/join logic.
- Station coverage is asymmetric by design: Hanoi has 2 PM2.5 stations, HCMC has 1, and HCMC PM10 is excluded (stale sensor). `mart_city_pm25_comparison` intentionally uses a station-balanced average.
- dbt `accepted_values` tests hardcode city names `Hanoi` and `Ho Chi Minh City`; changing labels/cities in `locations.yml` requires updating models/tests/dashboard.
- Ingestion modules are libraries, not CLIs; the DAG is the entrypoint. `ingestion/openaq/locations.py` discovery helpers are not used by the daily DAG.
- `.env` is gitignored and contains a live-looking OpenAQ key. Never print or commit it; note `.env.example` is currently gitignored/untracked too.
- Spec Kit is configured (`.opencode/commands/speckit.*`, `.github/skills/speckit-*`); feature specs belong under `specs/`. `.specify/` and `.opencode/` are gitignored.
