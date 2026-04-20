from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import pyodbc

def get_cbr_rates():
    # Настройки подключения для Docker -> Windows
    # host.docker.internal — это твой компьютер изнутри контейнера
    server = 'host.docker.internal,1433' 
    database = 'Car_Dealer_GA_CRM'
    username = 'airflow'
    password = 'airflow_pass'
    
    # Драйвер в Linux называется по-другому, чем в Windows!
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    response = requests.get(url)
    data = response.json()
    
    rate_date = datetime.strptime(data['Date'], '%Y-%m-%dT%H:%M:%S%z').date()
    currencies = ['USD', 'EUR']
    
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    for code in currencies:
        valute = data['Valute'][code]
        nominal = valute['Nominal']
        value = valute['Value']
        
        query = f"""
        IF EXISTS (SELECT 1 FROM CurrencyRates WHERE RateDate = '{rate_date}' AND CurrencyCode = '{code}')
        BEGIN
            UPDATE CurrencyRates SET RateValue = {value}, Nominal = {nominal}, UpdateTimestamp = GETDATE()
            WHERE RateDate = '{rate_date}' AND CurrencyCode = '{code}'
        END
        ELSE
        BEGIN
            INSERT INTO CurrencyRates (RateDate, CurrencyCode, Nominal, RateValue)
            VALUES ('{rate_date}', '{code}', {nominal}, {value})
        END
        """
        cursor.execute(query)

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Курсы на {rate_date} успешно обновлены.")

default_args = {
    'owner': 'Ilya',
    'start_date': datetime(2023, 10, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG('cbr_currency_update', 
         default_args=default_args, 
         schedule_interval='0 10 * * *', 
         catchup=False) as dag:

    task_get_rates = PythonOperator(
        task_id='fetch_and_save_rates',
        python_callable=get_cbr_rates
    )