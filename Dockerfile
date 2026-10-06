# Application image: ingestion jobs, dbt runner, Streamlit dashboard
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# System deps (libpq for psycopg2 build fallback, curl for healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# dbt project dir is mounted/run from /app/dbt/vietnam_air_quality
ENV DBT_PROFILES_DIR=/app/dbt/profiles

EXPOSE 8501

# Default: dashboard. Override per service in docker-compose.
CMD ["streamlit", "run", "dashboard/app.py", "--server.address=0.0.0.0", "--server.port=8501"]
