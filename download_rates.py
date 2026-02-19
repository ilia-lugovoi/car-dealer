import requests
import pyodbc
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime
import time

# 1. Настройки подключения
conn_str = (
    "Driver={SQL Server};"
    "Server=seaoffun\SQLEXPRESS;"
    "Database=Car_Dealer_GA_CRM;"
    "Trusted_Connection=yes;"
)

# 2. Диапазон дат (2020 год был високосным, так что 29 дней в феврале)
start_date = "2020-01-01"
end_date = "2020-02-29"
date_range = pd.date_range(start=start_date, end=end_date)

currencies = ['USD', 'EUR']

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

print("Начинаю загрузку данных...")

for current_date in date_range:
    # ЦБ принимает дату в формате ДД/ММ/ГГГГ
    formatted_date = current_date.strftime('%d/%m/%Y')
    url = f"http://www.cbr.ru/scripts/XML_daily.asp?date_req={formatted_date}"
    
    try:
        response = requests.get(url)
        # Декодируем из Windows-1251 (стандарт ЦБ)
        tree = ET.fromstring(response.content)
        
        for valute in tree.findall('Valute'):
            char_code = valute.find('CharCode').text
            
            if char_code in currencies:
                nominal = int(valute.find('Nominal').text)
                # В XML ЦБ цена идет с запятой, меняем на точку для SQL
                value = float(valute.find('Value').text.replace(',', '.'))
                
                # Записываем в базу (используем MERGE, чтобы не было ошибок PK)
                db_date = current_date.strftime('%Y-%m-%d')
                query = f"""
                MERGE CurrencyRates AS target
                USING (SELECT '{db_date}' AS r_date, '{char_code}' AS r_code) AS source
                ON (target.RateDate = source.r_date AND target.CurrencyCode = source.r_code)
                WHEN NOT MATCHED THEN
                    INSERT (RateDate, CurrencyCode, Nominal, RateValue)
                    VALUES ('{db_date}', '{char_code}', {nominal}, {value});
                """
                cursor.execute(query)
        
        print(f"Обработана дата: {formatted_date}")
        conn.commit()
        
        # Небольшая пауза, чтобы ЦБ нас не заблокировал
        time.sleep(0.1)
        
    except Exception as e:
        print(f"Ошибка на дате {formatted_date}: {e}")

cursor.close()
conn.close()
print("Загрузка исторически данных завершена!")
