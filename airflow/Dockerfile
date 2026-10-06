# Airflow image: official image + project Python deps
FROM apache/airflow:2.9.3-python3.11

USER root
RUN mkdir -p /opt/airflow/dags /opt/airflow/logs /opt/airflow/plugins \
    && chown -R airflow:0 /opt/airflow/dags /opt/airflow/logs /opt/airflow/plugins
USER airflow

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt dbt-postgres
