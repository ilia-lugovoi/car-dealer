from pathlib import Path
import pandas as pd
from ingestion.utils.logger import get_logger


logger = get_logger(__name__)


def extract_csv(path: Path) -> pd.DataFrame:

    if not path.exists():
        raise FileNotFoundError(
            f"CSV file not found: {path}"
        )

    logger.info("Reading CSV file: %s", path)

    df = pd.read_csv(
        path,
        encoding="cp1251",
        sep=";"
    )

    logger.info(
        "Extracted %s: %s rows, %s columns",
        path.name,
        len(df),
        len(df.columns),
    )

    return df


def extract_excel(path: Path) -> dict[str, pd.DataFrame]:

    if not path.exists():
        raise FileNotFoundError(
            f"Initial data file not found: {path}"
        )

    logger.info("Reading Excel file: %s", path)

    excel_file = pd.ExcelFile(path)

    logger.info(
        "Found sheets: %s",
        ", ".join(excel_file.sheet_names)
    )

    data = {}

    for sheet_name in excel_file.sheet_names:
        logger.info("Extracting sheet: %s", sheet_name)

        df = pd.read_excel(
            excel_file,
            sheet_name=sheet_name
        )

        data[sheet_name] = df

        logger.info(
            "Extracted %s: %s rows, %s columns",
            sheet_name,
            len(df),
            len(df.columns),
        )

    return data


def extract_sources(
    ga_sessions_path: Path,
    crm_events_path: Path,
    reference_data_path: Path,
) -> dict[str, pd.DataFrame]:

    data = {}

    # GA
    data["ga_sessions"] = extract_csv(
        ga_sessions_path
    )

    # CRM
    data["crm_events"] = extract_csv(
        crm_events_path
    )

    # Reference data
    reference_data = extract_excel(
        reference_data_path
    )

    data.update(reference_data)

    return data