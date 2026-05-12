from pathlib import Path
import pandas as pd
import urllib.parse
from sqlalchemy import create_engine

# Настройки путей
base_dir = Path.cwd()
data_path = base_dir / "CarDealer.xlsx"
output_dir = base_dir / "raw_data"
output_dir.mkdir(exist_ok=True) # Создать папку, если её нет

driver = "{ODBC Driver 17 for SQL Server}"
server = r"seaoffun\SQLEXPRESS" # Проверь имя своего сервера!
database = "car_dealer"

connection_string = (
    f"DRIVER={driver};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"Trusted_Connection=yes;"
)

print(f"Reading {data_path}...")
xlsx = pd.ExcelFile(data_path)

# Кодируем строку для SQLAlchemy
params = urllib.parse.quote_plus(connection_string)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

# Обходим каждый лист в книге
for sheet_name in xlsx.sheet_names:
    print(f"Processing sheet: {sheet_name}...")
    
    # Читаем лист в DataFrame
    df = pd.read_excel(xlsx, sheet_name=sheet_name)
    
    # --- ОПЦИОНАЛЬНО: Очистка имен столбцов ---
    # SQL не любит пробелы и точки в названиях колонок
    df.columns = [c.replace(' ', '_').replace('.', '_') for c in df.columns]

    # 3. Сохраняем в CSV (как ты и хотел, для архива)
    csv_file = output_dir / f"{sheet_name}.csv"
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    print(f"  - Saved to {csv_file}")

    # 4. Загружаем напрямую в MS SQL
    # if_exists='replace' создаст таблицу заново. 
    df.to_sql(sheet_name, engine, if_exists='replace', index=False)
    print(f"  - Uploaded to SQL table [{sheet_name}]")

print("\nDone! All sheets processed.")