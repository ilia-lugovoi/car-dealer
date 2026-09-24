from ingestion.config.settings import (
    GA_SESSIONS_PATH,
    CRM_EVENTS_PATH,
    REFERENCE_DATA_PATH,
)
from ingestion.extract.excel import extract_sources
from ingestion.load.postgres import (
    create_engine_connection,
    ensure_schema,
    load_table,
)
from ingestion.transform.clean import transform_dataframe
from ingestion.utils.logger import get_logger


logger = get_logger(__name__)


def main():
    logger.info("Starting car dealer ingestion")

    # 1. Extract
    data = extract_sources(
        ga_sessions_path=GA_SESSIONS_PATH,
        crm_events_path=CRM_EVENTS_PATH,
        reference_data_path=REFERENCE_DATA_PATH,
    )

    # 2. PostgreSQL
    engine = create_engine_connection()
    ensure_schema(engine)

    # 3. Transform + Load
    for table_name, df in data.items():

        transformed_df = transform_dataframe(
            df=df,
            table_name=table_name,
        )

        # PostgreSQL raw
        load_table(
            df=transformed_df,
            table_name=table_name,
            engine=engine,
        )

    logger.info(
        "Ingestion completed successfully"
    )


if __name__ == "__main__":
    main()