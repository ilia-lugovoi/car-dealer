# Сквозная аналитика автодилера

## О проекте
Проект моделирует сквозную аналитику автодилера от сырых данных до BI-витрин.

Источники в проекте:
- `CarDealer.xlsx` как исходный учебный датасет
- Google Analytics сессии
- CRM-события и продажи
- курсы валют ЦБ РФ

Цель проекта:
- собрать данные в MS SQL
- оркестрировать ежедневное обновление курсов через Airflow
- построить управляемый слой трансформаций через dbt
- подготовить BI-витрины для Power BI и Superset
- выгрузить итоговые витрины в ClickHouse

## Технологии
- MS SQL Server
- Python: `pyodbc`, `pandas`, `requests`, `openpyxl`
- Apache Airflow
- dbt (`dbt-sqlserver`)
- Docker
- ClickHouse
- Power BI
- Apache Superset

## Текущая архитектура
Пайплайн в проекте сейчас выглядит так:

1. Подготовка данных в `CarDealer.xlsx`
2. Скрипт [excel_to_db_csv.py](/C:/Users/ilyal/Documents/Доки/Кейсы/CarDealer/car-dealer/excel_to_db_csv.py)
   - загружает таблицы в MS SQL
   - параллельно сохраняет их в `csv`
3. Скрипт [update_rates.py](/C:/Users/ilyal/Documents/Доки/Кейсы/CarDealer/car-dealer/update_rates.py)
   - создаёт и обновляет `dbo.currency_rates`
   - забирает исторические и ежедневные курсы ЦБ РФ
4. Airflow DAG [auto_dealer_dag.py](/C:/Users/ilyal/Documents/Доки/Кейсы/CarDealer/car-dealer/airflow/dags/auto_dealer_dag.py)
   - ежедневно обновляет курсы
   - запускает `dbt build`
5. dbt-проект [car_dealer_dbt](/C:/Users/ilyal/Documents/Доки/Кейсы/CarDealer/car-dealer/car_dealer_dbt)
   - `staging` очищает источники
   - `intermediate` считает бизнес-логику
   - `marts/views` создаёт BI-view
6. Итоговые витрины:
   - `dbo.v_sessions`
   - `dbo.v_clients`
   - `dbo.v_medium`
7. Эти витрины вручную выгружаются в ClickHouse
8. ClickHouse используется как источник для Power BI и Superset

## dbt-слои
### `staging`
Grain и структура источников приводятся к удобному виду:
- `stg_ga_sessions`
- `stg_sales`
- `stg_models`
- `stg_currencies`
- `stg_currency_rates`
- `stg_clients`
- `stg_crm_events`
- `stg_mediums`

### `intermediate`
Промежуточная бизнес-логика:
- `int_models_with_currency`
- `int_session_crm`
- `int_sales`

В этом слое считаются:
- `price_rub`
- `gross_profit_rub`
- `ad_spend_share`

### `views`
Итоговые витрины для BI:
- `v_sessions`
  - grain: `1 row = 1 session`
- `v_clients`
  - grain: `1 row = 1 client_id`
- `v_medium`
  - grain: `1 row = 1 medium`

## Airflow
Airflow запущен в Docker и доступен по адресу:
- [http://localhost:8081](http://localhost:8081)

Используется для:
- ежедневной загрузки свежих курсов валют
- запуска `dbt build`

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

DDL-скрипты для ClickHouse лежат в:
- [sql/clickhouse](/C:/Users/ilyal/Documents/Доки/Кейсы/CarDealer/car-dealer/sql/clickhouse)

### Что важно при ручной загрузке CSV в ClickHouse
- сначала создаётся структура таблицы
- потом в неё загружаются данные
- для `SSMS`-CSV с `NULL` нужно использовать:
  - `--format_csv_null_representation='NULL'`
- для широкой витрины `v_sessions` лучше использовать `;` как разделитель
- при повторной полной загрузке таблицу лучше очищать через `TRUNCATE TABLE`

## BI
### Power BI
Power BI подключается к ClickHouse и использует:
- `v_sessions`
- `v_clients`
- `v_medium`

<!-- Добавить скрин подключения Power BI к ClickHouse -->
<!-- Добавить новый скрин модели данных Power BI -->
<!-- Добавить новые скрины визуализаций Power BI -->

### Superset
Superset запущен как отдельный сервис проекта в Docker и доступен по адресу:
- [http://localhost:8089/login/](http://localhost:8089/login/)

Используется для подключения к ClickHouse и построения альтернативных BI-визуализаций.

<!-- Добавить скрин подключения Superset к ClickHouse -->
<!-- Добавить скрин datasets в Superset -->
<!-- Добавить новые скрины дашборда Superset -->

## Docker-сервисы проекта
Текущий `docker-compose` поднимает:
- Airflow
- служебный Postgres для Airflow
- ClickHouse
- Superset
- служебный Postgres для Superset

## Как запустить проект
Из папки [car-dealer](/C:/Users/ilyal/Documents/Доки/Кейсы/CarDealer/car-dealer):

```powershell
docker compose up -d --build
```

После этого:
- Airflow: [http://localhost:8081](http://localhost:8081)
- Superset: [http://localhost:8089/login/](http://localhost:8089/login/)

## Что в проекте уже автоматизировано
- загрузка raw-данных из Excel в MS SQL
- выгрузка raw-таблиц в CSV
- создание и ежедневное обновление `currency_rates`
- трансформации и тесты в dbt

## Что сейчас делается вручную
- выгрузка `dbo.v_sessions`, `dbo.v_clients`, `dbo.v_medium` из MS SQL в CSV
- загрузка этих CSV в ClickHouse
- подключение ClickHouse к BI-инструментам

Это оставлено вручную специально как учебный этап, чтобы понять работу ClickHouse с нуля.
