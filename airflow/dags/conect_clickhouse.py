import clickhouse_connect

def mssql_to_clickhouse():
    # 1. Подключаемся к MS SQL (Источник)
    mssql_conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=host.docker.internal,1433;'
        'DATABASE=Car_Dealer_GA_CRM;'
        'UID=airflow;PWD=airflow_pass'
    )
    
    # 2. Подключаемся к ClickHouse (Хранилище)
    ch_client = clickhouse_connect.get_client(host='clickhouse', port=8123, username='default')

    tables = ['Client', 'Session', 'Model', 'Medium', 'CurrencyRates']

    for table in tables:
        # Читаем данные из MS SQL
        query = f"SELECT * FROM {table}"
        df = pd.read_sql(query, mssql_conn)
        
        # Создаем таблицу в ClickHouse «на лету» (для STG слоя)
        # ClickHouse сам поймет типы данных из Pandas
        ch_client.command(f'DROP TABLE IF EXISTS stg_{table}')
        ch_client.insert_df(f'stg_{table}', df)
        print(f"Таблица stg_{table} успешно перенесена в ClickHouse")

    mssql_conn.close()