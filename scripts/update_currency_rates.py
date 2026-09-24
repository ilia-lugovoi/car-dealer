import os
import xml.etree.ElementTree as ET
from datetime import date

import psycopg2
import requests
from dotenv import load_dotenv


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

load_dotenv(os.path.join(PROJECT_ROOT, ".env"))


POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "15432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "car_dealer")
POSTGRES_USER = os.getenv("POSTGRES_USER", "analytics")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")


CBR_URL = "https://www.cbr.ru/scripts/XML_daily.asp"


def get_connection():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
    )


def ensure_currency_rates_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS raw.currency_rates (
            rate_date DATE NOT NULL,
            currency_code VARCHAR(10) NOT NULL,
            nominal INTEGER NOT NULL,
            rate_value NUMERIC(18, 6) NOT NULL,
            update_timestamp TIMESTAMP NOT NULL
                DEFAULT CURRENT_TIMESTAMP,

            PRIMARY KEY (rate_date, currency_code)
        );
        """
    )


SUPPORTED_CURRENCY_CODES = ("USD", "EUR", "CNY")

def get_supported_currency_codes():
    return list(SUPPORTED_CURRENCY_CODES)

def get_rates_for_today(currencies):
    response = requests.get(
        CBR_URL,
        params={
            "date_req": date.today().strftime("%d/%m/%Y")
        },
        timeout=30,
    )

    response.raise_for_status()

    root = ET.fromstring(response.content)

    rate_date = date.today()
    rates = []

    for node in root.findall("Valute"):
        code = node.findtext("CharCode")

        if code not in currencies:
            continue

        nominal = int(
            node.findtext("Nominal")
        )

        value = float(
            node.findtext("Value").replace(",", ".")
        )

        rates.append(
            (
                code,
                nominal,
                value,
            )
        )

    return rate_date, rates


def upsert_rates(cursor, rate_date, rates):
    for code, nominal, value in rates:
        cursor.execute(
            """
            INSERT INTO raw.currency_rates (
                rate_date,
                currency_code,
                nominal,
                rate_value
            )
            VALUES (%s, %s, %s, %s)

            ON CONFLICT (
                rate_date,
                currency_code
            )

            DO UPDATE SET
                nominal = EXCLUDED.nominal,
                rate_value = EXCLUDED.rate_value,
                update_timestamp = CURRENT_TIMESTAMP;
            """,
            (
                rate_date,
                code,
                nominal,
                value,
            ),
        )


def main():
    print("Starting currency rates update...")

    conn = get_connection()

    try:
        with conn.cursor() as cursor:

            ensure_currency_rates_table(cursor)

            currency_codes = get_supported_currency_codes()

            print(
                f"Supported currencies: {currency_codes}"
            )

            rate_date, rates = get_rates_for_today(
                currencies=currency_codes
            )

            upsert_rates(
                cursor,
                rate_date,
                rates,
            )

            conn.commit()

            print(
                f"Updated rates for {rate_date}: "
                f"{len(rates)} records."
            )

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    main()