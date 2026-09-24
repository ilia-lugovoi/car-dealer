import csv
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import pyodbc
import requests


# Папки проекта
PROJECT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_DIR / "raw_data"
CLICKHOUSE_SQL_DIR = PROJECT_DIR / "sql" / "clickhouse"

# Подключение к ClickHouse по HTTP
CLICKHOUSE_URL = "http://127.0.0.1:8124/"
CLICKHOUSE_AUTH = ("analytics", "analytics")


def build_connection_string():
    """Локальное подключение к MSSQL с ноутбука."""
    return (
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=seaoffun\\SQLEXPRESS;"
        "Database=car_dealer;"
        "Trusted_Connection=yes;"
        "Encrypt=no;"
    )


def format_value(value):
    """Приводим значения MSSQL к строкам для CSV."""
    if value is None:
        return "NULL"
    if isinstance(value, datetime):
        return value.strftime("%d.%m.%Y %H:%M:%S")
    if isinstance(value, date):
        return value.strftime("%d.%m.%Y")
    if isinstance(value, Decimal):
        return format(value, "f")
    return str(value)


def export_query_to_csv(cursor, query, file_path, delimiter):
    """Выгружаем результат SQL-запроса в CSV."""
    rows = cursor.execute(query).fetchall()

    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)
        for row in rows:
            writer.writerow([format_value(value) for value in row])

    print(f"CSV создан: {file_path}")


def export_views_from_mssql():
    """Создаем свежие CSV по BI-витринам из MSSQL."""
    conn = pyodbc.connect(build_connection_string())
    cursor = conn.cursor()

    export_query_to_csv(
        cursor,
        "SELECT medium_name, medium_group_id, medium_sort FROM dbo.v_medium ORDER BY medium_sort, medium_name",
        RAW_DIR / "v_medium.csv",
        ",",
    )

    export_query_to_csv(
        cursor,
        "SELECT medium_group_name, medium_group_sort FROM dbo.v_medium_groups ORDER BY medium_group_sort, medium_group_name",
        RAW_DIR / "v_medium_groups.csv",
        ",",
    )

    export_query_to_csv(
        cursor,
        """
        SELECT
            client_id,
            sessions_cnt,
            total_pageviews,
            total_conversions,
            total_ad_cost,
            first_session_date,
            last_session_date,
            sales_cnt,
            total_price_rub,
            total_gross_profit_rub,
            total_contribution_margin_rub,
            last_sale_date
        FROM dbo.v_clients
        ORDER BY client_id
        """,
        RAW_DIR / "v_clients.csv",
        ",",
    )

    export_query_to_csv(
        cursor,
        """
        SELECT
            id,
            client_id,
            domain,
            city,
            region,
            browser,
            device_category,
            [date],
            CONVERT(varchar(10), date_dt, 23) as date_dt,
            pageviews,
            campaign,
            keyword,
            medium,
            medium_group,
            source,
            sessions,
            goal_completion_location,
            conversion,
            source_conv,
            ad_cost,
            sale,
            model_ga_name,
            crm_city,
            count_cost,
            dealer_meet,
            crm_sale,
            brand_name,
            class_name,
            model_name,
            price_original,
            currency_code,
            price_rub,
            gross_profit_rub,
            contribution_margin_rub
        FROM dbo.v_sessions
        ORDER BY id
        """,
        RAW_DIR / "v_sessions_sc.csv",
        ";",
    )

    cursor.close()
    conn.close()


def clickhouse_post(sql, data=None, settings=None):
    """Выполняем запрос в ClickHouse через HTTP."""
    params = {"database": "car_dealer", "query": sql} if data is not None else {"database": "car_dealer"}
    if settings:
        params.update(settings)

    response = requests.post(
        CLICKHOUSE_URL,
        params=params,
        data=data if data is not None else sql,
        auth=CLICKHOUSE_AUTH,
        timeout=120,
    )
    if not response.ok:
        raise RuntimeError(response.text)
    return response.text


def recreate_clickhouse_tables():
    """Удаляем старые таблицы и создаем их заново по DDL-скриптам."""
    clickhouse_post("DROP TABLE IF EXISTS v_medium")
    clickhouse_post("DROP TABLE IF EXISTS v_medium_groups")
    clickhouse_post("DROP TABLE IF EXISTS v_clients")
    clickhouse_post("DROP TABLE IF EXISTS v_sessions")

    clickhouse_post((CLICKHOUSE_SQL_DIR / "create_v_medium.sql").read_text(encoding="utf-8"))
    clickhouse_post((CLICKHOUSE_SQL_DIR / "create_v_medium_groups.sql").read_text(encoding="utf-8"))
    clickhouse_post((CLICKHOUSE_SQL_DIR / "create_v_clients.sql").read_text(encoding="utf-8"))
    clickhouse_post((CLICKHOUSE_SQL_DIR / "create_v_sessions.sql").read_text(encoding="utf-8"))

    print("Таблицы ClickHouse пересозданы.")


def load_csv_to_clickhouse():
    """Загружаем подготовленные CSV в ClickHouse."""
    clickhouse_post(
        "INSERT INTO v_medium FORMAT CSV",
        data=(RAW_DIR / "v_medium.csv").read_bytes(),
    )

    clickhouse_post(
        "INSERT INTO v_medium_groups FORMAT CSV",
        data=(RAW_DIR / "v_medium_groups.csv").read_bytes(),
    )

    clickhouse_post(
        "INSERT INTO v_clients FORMAT CSV",
        data=(RAW_DIR / "v_clients.csv").read_bytes(),
        settings={"format_csv_null_representation": "NULL"},
    )

    clickhouse_post(
        "INSERT INTO v_sessions FORMAT CSV",
        data=(RAW_DIR / "v_sessions_sc.csv").read_bytes(),
        settings={
            "format_csv_delimiter": ";",
            "format_csv_null_representation": "NULL",
        },
    )

    print("CSV загружены в ClickHouse.")


def print_row_counts():
    """Печатаем количество строк для быстрой проверки."""
    for table_name in ("v_medium", "v_medium_groups", "v_clients", "v_sessions"):
        rows = clickhouse_post(f"SELECT count() FROM {table_name}").strip()
        print(f"{table_name}: {rows}")


def main():
    # 1. Выгружаем витрины из MSSQL в CSV
    export_views_from_mssql()

    # 2. Пересоздаем таблицы в ClickHouse
    recreate_clickhouse_tables()

    # 3. Загружаем данные в ClickHouse
    load_csv_to_clickhouse()

    # 4. Проверяем количество строк
    print_row_counts()


if __name__ == "__main__":
    main()
