import pandas as pd
from sqlalchemy import create_engine, text

from ingestion.config.settings import (
    POSTGRES_URL,
    RAW_SCHEMA,
)
from ingestion.utils.logger import get_logger


logger = get_logger(__name__)

def create_engine_connection():
    logger.info("Creating PostgreSQL connection")

    return create_engine(
        POSTGRES_URL,
        pool_pre_ping=True,
    )

def ensure_schema(engine):
    with engine.begin() as connection:
        connection.execute(
            text(f"CREATE SCHEMA IF NOT EXISTS {RAW_SCHEMA}")
        )

    logger.info(
        "Schema '%s' is ready",
        RAW_SCHEMA,
    )

def load_table(
    df: pd.DataFrame,
    table_name: str,
    engine,
):
    logger.info(
        "Loading table raw.%s",
        table_name,
    )

    df.to_sql(
        name=table_name,
        con=engine,
        schema=RAW_SCHEMA,
        if_exists="replace",
        index=False,
        method="multi",
    )

    logger.info(
        "Loaded raw.%s: %s rows",
        table_name,
        len(df),
    )