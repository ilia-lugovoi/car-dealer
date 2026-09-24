import os

SQLALCHEMY_DATABASE_URI = os.getenv(
    "SUPERSET_DATABASE_URI"
)

SECRET_KEY = os.getenv(
    "SUPERSET_SECRET_KEY"
)

# For local project usage this keeps the setup predictable.
WTF_CSRF_ENABLED = True
TALISMAN_ENABLED = False