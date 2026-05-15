# Сквозная аналитика автодилера

## Цели проекта:
1) Создать эффективную, управляемую, масштабируемую и безопасную архитектуру данных для автодилера (данные из Google Analyst, CRM, продаж и справочника)
2) Создать дашборд анализа продаж и рекламы, чтобы оценить эффективность интернет-рекламы и найти точки роста

## Технологии

### Архитектура данных:
MS SQL, Python (pandas, requests, pyodbc, openpyxl), Airflow, dbt, ClickHouse, Docker, Excel, Power Query

### BI-решения:
Power BI (DAX) и Apache Superset (SQL Lab)

## Пайплайн проекта

1. Подготовка данных в Excel с помощью Power Query из `источник.xlsx` в `CarDealer.xlsx`

   <img width="1461" height="732" alt="преобразование" src="https://github.com/user-attachments/assets/e6aa4a93-eac5-49ef-8738-1beb2f4e4e3d" />


3. Перенос данных из Excel в MS SQL и сохранение в csv с помощью Python

   [excel_to_db_csv.py](./scripts/excel_to_db_csv.py)


4. Создаем таблицу currency_rates и выгружаем курсы валют с сайта ЦБ РФ за необходимый период

   [backfill_currency_rates.py](./scripts/backfill_currency_rates.py)


5. Запускаем dbt и автоматическое обновление курсов валют с сайта ЦБ с помощью Airflow

   [auto_dealer_dag.py](./airflow/dags/auto_dealer_dag.py)


6. Создаем слои с витринами в dbt

   [car_dealer_dbt](./car_dealer_dbt)


7. Подключаемся к ClickHouse, создаем таблицы и загружаем в них витрины

   [load_clickhouse_views.py](./scripts/load_clickhouse_views.py)


## dbt-слои
### `staging`
Grain и структура источников приводятся к удобному виду:

### `intermediate`
Промежуточная бизнес-логика:

В этом слое считаются:

### `views`
Итоговые витрины для BI:

## Airflow
Airflow запущен в Docker и доступен по адресу:
[http://localhost:8081](http://localhost:8081)

Используется для:

## ClickHouse
ClickHouse запущен как отдельный сервис проекта в Docker.

Порты проекта:
- HTTP: `8124`
- Native: `9001`

Параметры подключения:
- host: `127.0.0.1`
- database: `car_dealer`
- user: `analytics`
- password: `analytics`

DDL-скрипты для ClickHouse лежат в папке:
[sql/clickhouse](./sql/clickhouse)

### Собранные пометки, используемые в скриптах:
1. Для `SSMS`-CSV с `NULL` нужно использовать:
   `--format_csv_null_representation='NULL'`
2. Для широкой витрины `v_sessions` нужно использовать `;` как разделитель
3. При повторной полной загрузке таблицу лучше очищать через `TRUNCATE TABLE`

## BI
### Power BI


### Superset
Superset доступен по адресу:

Используется для подключения к ClickHouse и построения альтернативных BI-визуализаций.


## Docker-сервисы проекта
Текущий `docker-compose` поднимает:

## Как запустить проект

