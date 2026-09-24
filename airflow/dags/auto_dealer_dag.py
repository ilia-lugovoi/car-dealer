import os
import subprocess
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator


PROJECT_DIR = "/opt/airflow/project"

DBT_PROJECT_DIR = os.path.join(
    PROJECT_DIR,
    "dbt_project",
)

DBT_PROFILES_DIR = os.path.join(
    PROJECT_DIR,
    "dbt_project",
)

default_args = {
    "owner": "Ilya",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def update_currency_rates():
    script_path = os.path.join(
        PROJECT_DIR,
        "scripts",
        "update_currency_rates.py",
    )

    subprocess.run(
        [
            "python",
            script_path,
        ],
        check=True,
    )


def run_dbt_build():
    subprocess.run(
        [
            "dbt",
            "build",
            "--project-dir",
            DBT_PROJECT_DIR,
            "--profiles-dir",
            DBT_PROFILES_DIR,
        ],
        check=True,
    )


with DAG(
    dag_id="auto_dealer",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule="0 10 * * *",
    catchup=False,
    description=(
        "Daily currency rates update "
        "and dbt build for auto dealer analytics."
    ),
    tags=[
        "auto_dealer",
        "currency",
        "dbt",
    ],
) as dag:

    update_currency_rates_task = PythonOperator(
        task_id="update_currency_rates",
        python_callable=update_currency_rates,
    )

    dbt_build_task = PythonOperator(
        task_id="dbt_build",
        python_callable=run_dbt_build,
    )

    update_currency_rates_task >> dbt_build_task