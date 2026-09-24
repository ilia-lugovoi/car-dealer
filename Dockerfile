FROM apache/airflow:2.10.5-python3.11

USER airflow

RUN pip install --no-cache-dir \
    dbt-postgres \
    psycopg2-binary==2.9.12 \
    requests \
    python-dotenv