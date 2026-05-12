SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://superset:superset@superset_db:5432/superset"
SECRET_KEY = "car_dealer_superset_secret_key"

# For local project usage this keeps the setup predictable.
WTF_CSRF_ENABLED = True
TALISMAN_ENABLED = False
