from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator


default_args = {
    "owner": "Ilya",
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="car_dealer_mssql_dbt",
    default_args=default_args,
    schedule_interval="0 10 * * *",
    catchup=False,
    description="Ежедневное обновление курсов ЦБ и пересборка dbt-моделей для car_dealer в MS SQL.",
) as dag:
    update_currency_rates = BashOperator(
        task_id="update_currency_rates",
        bash_command="cd /opt/airflow/project && python update_rates.py --mode daily",
    )

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command="cd /opt/airflow/project && dbt build --project-dir car_dealer_dbt --profiles-dir car_dealer_dbt",
    )

    update_currency_rates >> dbt_build
