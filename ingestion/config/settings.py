from pathlib import Path
import os
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

# Source
SOURCE_DATA_PATH = PROJECT_ROOT / "data"

GA_SESSIONS_PATH = SOURCE_DATA_PATH / "ga_sessions.csv"
CRM_EVENTS_PATH = SOURCE_DATA_PATH / "crm_events.csv"
REFERENCE_DATA_PATH = SOURCE_DATA_PATH / "reference_data.xlsx"

# PostgreSQL
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "car_dealer")
POSTGRES_USER = os.getenv("POSTGRES_USER", "analytics")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

POSTGRES_URL = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# Schemas
RAW_SCHEMA = "raw"