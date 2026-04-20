FROM apache/airflow:2.7.1

USER root

# Устанавливаем системные зависимости для драйвера MSSQL
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    ca-certificates \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev \
    && apt-get clean

USER airflow

# Устанавливаем библиотеки Python
RUN pip install pyodbc requests
RUN pip install pyodbc requests clickhouse-connect