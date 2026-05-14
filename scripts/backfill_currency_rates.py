import requests
import pyodbc
import xml.etree.ElementTree as ET
from datetime import timedelta


# Подключение к MSSQL
conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=seaoffun\\SQLEXPRESS;"
    "Database=car_dealer;"
    "Trusted_Connection=yes;"
)

archive_url = "https://www.cbr.ru/scripts/XML_daily.asp"


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


def get_project_date_range(cursor):
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
    return row.start_date, row.end_date


def get_rates_for_date(rate_date, currencies):
    response = requests.get(
        archive_url,
        params={"date_req": rate_date.strftime("%d/%m/%Y")},
        timeout=30,
    )
    response.raise_for_status()

    root = ET.fromstring(response.content)
    rates = []

    for node in root.findall("Valute"):
        code = node.findtext("CharCode")
        if code not in currencies:
            continue

        nominal = int(node.findtext("Nominal"))
        value = float(node.findtext("Value").replace(",", "."))
        rates.append((code, nominal, value))

    return rates


def upsert_rates(cursor, rate_date, rates):
    for code, nominal, value in rates:
        query = """
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
        cursor.execute(query, rate_date, code, nominal, value)


def main():
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    ensure_currency_rates_table(cursor)

    currencies = get_supported_currency_codes(cursor)
    start_date, end_date = get_project_date_range(cursor)

    current_date = start_date
    rows_written = 0

    while current_date <= end_date:
        rates = get_rates_for_date(current_date, currencies)
        upsert_rates(cursor, current_date, rates)
        rows_written += len(rates)
        current_date += timedelta(days=1)

    conn.commit()
    cursor.close()
    conn.close()

    print(f"Курсы за период {start_date} - {end_date} успешно загружены. Записей: {rows_written}")


if __name__ == "__main__":
    main()
