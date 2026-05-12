import argparse
import os
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta

import pyodbc
import requests


CURRENT_RATES_URL = "https://www.cbr-xml-daily.ru/daily_json.js"
ARCHIVE_RATES_URL = "https://www.cbr.ru/scripts/XML_daily.asp"
DEFAULT_SERVER = r"seaoffun\SQLEXPRESS"
DEFAULT_DATABASE = "car_dealer"
DEFAULT_CURRENCIES = ["CNY", "USD", "EUR", "RUB"]


def env_flag(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y"}


def build_connection_string() -> str:
    server = os.getenv("MSSQL_SERVER", DEFAULT_SERVER)
    database = os.getenv("MSSQL_DATABASE", DEFAULT_DATABASE)
    driver = os.getenv("MSSQL_DRIVER", "ODBC Driver 18 for SQL Server")
    trusted = env_flag("MSSQL_TRUSTED_CONNECTION", True)
    user = os.getenv("MSSQL_USER")
    password = os.getenv("MSSQL_PASSWORD")

    parts = [
        f"DRIVER={{{driver}}}",
        f"SERVER={server}",
        f"DATABASE={database}",
        "Encrypt=yes",
        "TrustServerCertificate=yes",
    ]

    if user and password:
        parts.extend([f"UID={user}", f"PWD={password}"])
    elif trusted:
        parts.append("Trusted_Connection=yes")

    return ";".join(parts)


def connect():
    return pyodbc.connect(build_connection_string())


def ensure_currency_rates_table(cursor) -> None:
    cursor.execute(
        """
        IF EXISTS (SELECT 1 FROM sys.objects WHERE object_id = OBJECT_ID(N'dbo.CurrencyRates') AND type = 'U')
           AND NOT EXISTS (
               SELECT 1
               FROM sys.tables
               WHERE schema_id = SCHEMA_ID('dbo')
                 AND name COLLATE Latin1_General_CS_AS = 'currency_rates'
           )
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM sys.key_constraints
                WHERE parent_object_id = OBJECT_ID(N'dbo.CurrencyRates')
            )
            BEGIN
                DECLARE @pk_name sysname;
                SELECT TOP (1) @pk_name = kc.name
                FROM sys.key_constraints kc
                WHERE kc.parent_object_id = OBJECT_ID(N'dbo.CurrencyRates');

                EXEC('ALTER TABLE dbo.CurrencyRates DROP CONSTRAINT [' + @pk_name + ']');
            END

            EXEC sp_rename 'dbo.CurrencyRates', 'currency_rates_tmp';
            EXEC sp_rename 'dbo.currency_rates_tmp', 'currency_rates';
        END

        IF NOT EXISTS (
            SELECT 1
            FROM sys.tables
            WHERE schema_id = SCHEMA_ID('dbo')
              AND name COLLATE Latin1_General_CS_AS = 'currency_rates'
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

        IF EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'dbo.currency_rates') AND name = 'RateDate')
            EXEC sp_rename 'dbo.currency_rates.RateDate', 'rate_date', 'COLUMN';

        IF EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'dbo.currency_rates') AND name = 'CurrencyCode')
            EXEC sp_rename 'dbo.currency_rates.CurrencyCode', 'currency_code', 'COLUMN';

        IF EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'dbo.currency_rates') AND name = 'Nominal')
            EXEC sp_rename 'dbo.currency_rates.Nominal', 'nominal', 'COLUMN';

        IF EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'dbo.currency_rates') AND name = 'RateValue')
            EXEC sp_rename 'dbo.currency_rates.RateValue', 'rate_value', 'COLUMN';

        IF EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'dbo.currency_rates') AND name = 'UpdateTimestamp')
            EXEC sp_rename 'dbo.currency_rates.UpdateTimestamp', 'update_timestamp', 'COLUMN';
        """
    )


def get_supported_currency_codes(cursor) -> list[str]:
    try:
        rows = cursor.execute(
            "SELECT currency_code FROM dbo.currencies ORDER BY id"
        ).fetchall()
        codes = [row[0] for row in rows if row[0]]
    except pyodbc.Error:
        codes = DEFAULT_CURRENCIES.copy()

    if "RUB" not in codes:
        codes.append("RUB")

    return sorted(set(codes))


def get_project_date_range(cursor) -> tuple[date, date]:
    row = cursor.execute(
        """
        SELECT
            MIN(min_dt) AS start_date,
            MAX(max_dt) AS end_date
        FROM (
            SELECT MIN(CAST([date] AS date)) AS min_dt, MAX(CAST([date] AS date)) AS max_dt
            FROM dbo.ga_sessions
            UNION ALL
            SELECT MIN(CAST(sale_date AS date)) AS min_dt, MAX(CAST(sale_date AS date)) AS max_dt
            FROM dbo.sales
        ) src
        """
    ).fetchone()

    if not row or not row.start_date or not row.end_date:
        raise ValueError("Не удалось определить диапазон дат проекта из таблиц ga_sessions и sales.")

    return row.start_date, row.end_date


def fetch_current_rates(codes: list[str]) -> tuple[date, list[tuple[str, int, float]]]:
    response = requests.get(CURRENT_RATES_URL, timeout=30)
    response.raise_for_status()
    payload = response.json()

    rate_date = datetime.strptime(payload["Date"], "%Y-%m-%dT%H:%M:%S%z").date()
    result = []

    for code in codes:
        if code == "RUB":
            result.append((code, 1, 1.0))
            continue

        valute = payload["Valute"].get(code)
        if not valute:
            continue

        result.append((code, int(valute["Nominal"]), float(valute["Value"])))

    return rate_date, result


def fetch_archive_rates(rate_date: date, codes: list[str]) -> list[tuple[str, int, float]]:
    result = [("RUB", 1, 1.0)] if "RUB" in codes else []

    response = requests.get(
        ARCHIVE_RATES_URL,
        params={"date_req": rate_date.strftime("%d/%m/%Y")},
        timeout=30,
    )
    response.raise_for_status()

    root = ET.fromstring(response.content)
    wanted = {code for code in codes if code != "RUB"}

    for node in root.findall("Valute"):
        char_code = node.findtext("CharCode")
        if char_code not in wanted:
            continue

        nominal = int(node.findtext("Nominal"))
        value = float(node.findtext("Value").replace(",", "."))
        result.append((char_code, nominal, value))

    return result


def upsert_rates(cursor, rate_date: date, rates: list[tuple[str, int, float]]) -> int:
    written = 0
    merge_sql = """
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
    """

    for code, nominal, value in rates:
        cursor.execute(merge_sql, rate_date, code, nominal, value)
        written += 1

    return written


def run_daily(cursor, codes: list[str]) -> int:
    rate_date, rates = fetch_current_rates(codes)
    written = upsert_rates(cursor, rate_date, rates)
    print(f"Обновлены курсы за {rate_date}: {written} записей.")
    return written


def run_backfill(cursor, codes: list[str], start_date: date | None, end_date: date | None) -> int:
    if start_date is None or end_date is None:
        start_date, end_date = get_project_date_range(cursor)

    written_total = 0
    current_date = start_date

    while current_date <= end_date:
        rates = fetch_archive_rates(current_date, codes)
        if rates:
            written_total += upsert_rates(cursor, current_date, rates)
        current_date += timedelta(days=1)

    print(f"Заполнены исторические курсы с {start_date} по {end_date}: {written_total} записей.")
    return written_total


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["daily", "backfill"],
        default="daily",
        help="daily обновляет курсы за текущую дату ЦБ, backfill заполняет исторический диапазон проекта.",
    )
    parser.add_argument("--start-date", type=lambda s: datetime.strptime(s, "%Y-%m-%d").date())
    parser.add_argument("--end-date", type=lambda s: datetime.strptime(s, "%Y-%m-%d").date())
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    with connect() as conn:
        cursor = conn.cursor()
        ensure_currency_rates_table(cursor)
        codes = get_supported_currency_codes(cursor)

        if args.mode == "backfill":
            run_backfill(cursor, codes, args.start_date, args.end_date)
        else:
            run_daily(cursor, codes)

        conn.commit()


if __name__ == "__main__":
    main()
