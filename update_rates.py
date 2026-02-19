import requests
import pyodbc
from datetime import datetime

conn_str = (
    "Driver={SQL Server};"
    "Server=seaoffun\SQLEXPRESS;"
    "Database=Car_Dealer_GA_CRM;"
    "Trusted_Connection=yes;" # Если используете Windows-авторизацию
)

url = "https://www.cbr-xml-daily.ru/daily_json.js"
response = requests.get(url)
data = response.json()

rate_date = datetime.strptime(data['Date'], '%Y-%m-%dT%H:%M:%S%z').date()
currencies = ['USD', 'EUR'] # Добавьте нужные коды

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

for code in currencies:
    valute = data['Valute'][code]
    nominal = valute['Nominal']
    value = valute['Value']
    
    # Используем MERGE (UPSERT), чтобы не дублировать записи при повторном запуске
    query = f"""
    MERGE CurrencyRates AS target
    USING (SELECT '{rate_date}' AS r_date, '{code}' AS r_code) AS source
    ON (target.RateDate = source.r_date AND target.CurrencyCode = source.r_code)
    WHEN MATCHED THEN
        UPDATE SET RateValue = {value}, Nominal = {nominal}, UpdateTimestamp = GETDATE()
    WHEN NOT MATCHED THEN
        INSERT (RateDate, CurrencyCode, Nominal, RateValue)
        VALUES ('{rate_date}', '{code}', {nominal}, {value});
    """
    cursor.execute(query)

conn.commit()
cursor.close()
conn.close()
print(f"Курсы на {rate_date} успешно обновлены.")