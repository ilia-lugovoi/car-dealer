import re
import pandas as pd
from ingestion.utils.logger import get_logger


logger = get_logger(__name__)

def normalize_column_name(column: str) -> str:
    """
    Converts column name to snake_case.
    """

    column = str(column).strip().lower()

    column = re.sub(
        r"[^a-zA-Z0-9_]+",
        "_",
        column,
    )

    column = re.sub(
        r"_+",
        "_",
        column,
    )

    return column.strip("_")


def transform_dataframe(
    df: pd.DataFrame,
    table_name: str,
) -> pd.DataFrame:

    result = df.copy()

    result.columns = [
        normalize_column_name(column)
        for column in result.columns
    ]

    for column in result.columns:
        if column in {"date", "sale_date"}:
            result[column] = pd.to_datetime(
                result[column],
                errors="coerce",
            )

    logger.info(
        "Transformed %s: %s rows, %s columns",
        table_name,
        len(result),
        len(result.columns),
    )

    return result