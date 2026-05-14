import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
import pyodbc
import requests

CURRENT_RATES_URL = "https://www.cbr-xml-daily.ru/daily_json.js"

default_args = {
    "owner": "Ilya",
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def build_connection_string():
    return (
        f"DRIVER={{{os.getenv('MSSQL_DRIVER', 'ODBC Driver 18 for SQL Server')}}};"
        f"SERVER={os.getenv('MSSQL_SERVER', 'host.docker.internal')},{os.getenv('MSSQL_PORT', '1433')};"
        f"DATABASE={os.getenv('MSSQL_DATABASE', 'car_dealer')};"
        f"UID={os.getenv('MSSQL_USER', 'airflow')};"
        f"PWD={os.getenv('MSSQL_PASSWORD', 'airflow_pass')};"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
    )


def connect():
    return pyodbc.connect(build_connection_string())


def ensure_currency_rates_table(cursor):
    cursor.execute(
        """
        IF NOT EXISTS (
            SELECT 1
            FROM sys.tables
            WHERE schema_id = SCHEMA_ID('dbo')
              AND name = 'currency_rates'
        )
        BEGIN
            CREATE TABLE dbo.currency_rates (
                rate_date date NOT NULL,
                currency_code varchar(10) NOT NULL,
                nominal int NOT NULL,
                rate_value decimal(18, 6) NOT NULL,
                update_timestamp datetime2 NOT NULL DEFAULT SYSDATETIME()
            );
        END
        """
    )


def get_supported_currency_codes(cursor):
    rows = cursor.execute(
        """
        SELECT currency_code
        FROM dbo.currencies
        WHERE currency_code <> 'RUB'
        ORDER BY id
        """
    ).fetchall()
    return [row[0] for row in rows]


def upsert_rates(cursor, rate_date, rates):
    written = 0

    for code, nominal, value in rates:
        cursor.execute(
            """
            MERGE dbo.currency_rates AS target
            USING (
                SELECT
                    CAST(? AS date) AS rate_date,
                    CAST(? AS varchar(10)) AS currency_code,
                    CAST(? AS int) AS nominal,
                    CAST(? AS decimal(18, 6)) AS rate_value
            ) AS source
            ON target.rate_date = source.rate_date
           AND target.currency_code = source.currency_code
            WHEN MATCHED THEN
                UPDATE SET
                    nominal = source.nominal,
                    rate_value = source.rate_value,
                    update_timestamp = SYSDATETIME()
            WHEN NOT MATCHED THEN
                INSERT (rate_date, currency_code, nominal, rate_value)
                VALUES (source.rate_date, source.currency_code, source.nominal, source.rate_value);
            """,
            rate_date,
            code,
            nominal,
            value,
        )
        written += 1

    return written


def fetch_current_rates(codes: list[str]):
    response = requests.get(CURRENT_RATES_URL, timeout=30)
    response.raise_for_status()
    payload = response.json()

    rate_date = datetime.strptime(payload["Date"], "%Y-%m-%dT%H:%M:%S%z").date()
    result = []

    for code in codes:
        valute = payload["Valute"].get(code)
        if not valute:
            continue

        result.append((code, int(valute["Nominal"]), float(valute["Value"])))

    return rate_date, result


def update_currency_rates_daily():
    with connect() as conn:
        cursor = conn.cursor()
        ensure_currency_rates_table(cursor)
        codes = get_supported_currency_codes(cursor)
        rate_date, rates = fetch_current_rates(codes)
        written = upsert_rates(cursor, rate_date, rates)
        conn.commit()
        print(f"Обновлены курсы за {rate_date}: {written} записей.")


with DAG(
    dag_id="car_dealer_mssql_dbt",
    default_args=default_args,
    schedule_interval="0 10 * * *",
    catchup=False,
    description="Ежедневное обновление курсов ЦБ и пересборка dbt-моделей для car_dealer в MS SQL.",
) as dag:
    update_currency_rates = PythonOperator(
        task_id="update_currency_rates",
        python_callable=update_currency_rates_daily,
    )

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command="cd /opt/airflow/project && dbt build --project-dir car_dealer_dbt --profiles-dir car_dealer_dbt",
    )

    update_currency_rates >> dbt_build
