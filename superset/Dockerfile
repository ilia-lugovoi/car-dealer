FROM apache/superset:4.1.1

USER root

RUN pip install --no-cache-dir \
    clickhouse-connect \
    psycopg2-binary

USER superset

COPY superset/superset_config.py /app/pythonpath/superset_config.py
