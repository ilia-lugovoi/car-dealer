# Analytics for Auto Dealerships

BI-решение для анализа продаж и эффективности интернет-рекламы автодилера.

Проект построен как end-to-end аналитический pipeline:
от загрузки исходных данных и контроля качества до формирования
аналитических витрин и интерактивных Power BI-отчётов.

> **Данные:** обезличированный тестовый набор данных.

---

## Цели проекта

Проект решает две основные аналитические задачи:

1. **Анализ продаж**
   - сколько автомобилей продано;
   - на какую сумму;
   - какая маржинальная прибыль;
   - как меняются продажи по городам и моделям.

2. **Анализ эффективности интернет-рекламы**
   - откуда приходит трафик;
   - какие каналы приводят к продажам;
   - как проходит пользовательская воронка;
   - сколько стоит привлечение;
   - сколько маржинальной прибыли приносит 1 ₽ рекламных расходов.

---

## Архитектура

```text
                Исходные данные
             CSV / Excel / CRM / GA
                       │
                       ▼
                Python ingestion
             Extract → Transform → Load
                       │
                       ▼
                  PostgreSQL
                       │
                 ┌─────┴─────┐
                 │    raw    │
                 └─────┬─────┘
                       │
                       ▼
                      dbt
                       │
              ┌────────┴────────┐
              ▼                 ▼
          staging              marts
              │                 │
              └────────┬────────┘
                       ▼
                Power BI
                 semantic model
                       │
              ┌────────┴────────┐
              ▼                 ▼
          Продажи          Интернет-реклама
```

ClickHouse и Apache Superset рассматриваются как дополнительный
аналитический слой проекта и развиваются отдельно.

---

## Технологии

### Data Engineering
- Python
- pandas
- PostgreSQL
- SQLAlchemy
- psycopg2
- Docker
- Apache Airflow

### Analytics Engineering
- dbt
- dbt tests
- dbt documentation
- PostgreSQL

### BI
- Power BI
- DAX
- Apache Superset — WIP

### Дополнительно
- ClickHouse — WIP
- Git / GitHub

---

## Data Pipeline

### 1. Ingestion

Python-пайплайн загружает исходные данные из CSV и Excel.

Основные этапы:

``` text
   Extract
      ↓
   Transform
      ↓
   Load
      ↓
   PostgreSQL raw
```

**В ingestion реализованы:**
- централизованная конфигурация;
- логирование;
- проверка наличия файлов;
- нормализация исходных данных;
- загрузка таблиц в PostgreSQL.

Запуск:
``` python
python -m ingestion.main
```

### 2. PostgreSQL

PostgreSQL используется как основное хранилище проекта.

Исходные данные загружаются в raw schema.

``` text
PostgreSQL
└── raw
    ├── ga_sessions
    ├── crm_events
    ├── clients
    ├── models
    ├── brands
    ├── classes
    ├── mediums
    ├── medium_groups
    ├── prices
    └── currency_rates
```

### dbt
dbt используется для аналитического преобразования данных.

#### Staging

На staging-слое:
- приводятся типы данных;
- нормализуются названия колонок;
- стандартизируются значения;
- формируются аналитические ключи;
- выполняются проверки качества данных.

Основные модели:
```text
stg_ga_sessions
stg_crm_events
stg_clients
stg_models
stg_brands
stg_classes
stg_mediums
stg_medium_groups
stg_prices
stg_currency_rates
```

Для моделей используются dbt tests:
- `not_null`
- `unique`
- `relationships`
- `accepted_values`

#### Marts

`mart_sales`
Витрина для анализа продаж.

Основные показатели:
- количество продаж;
- стоимость автомобиля;
- маржинальная прибыль;
- рекламные расходы;
- contribution margin;
- город;
- бренд;
- модель;
- класс автомобиля.

Grain:
```text
1 строка = 1 продажа
```

`mart_ad_effectiveness`
Витрина для анализа интернет-рекламы.

Основные показатели:
- sessions;
- conversion;
- dealer meetings;
- estimates;
- sales;
- ad cost;
- margin;
- contribution margin;
- pageviews;
- pageviews per session.

Основные измерения:
- medium;
- campaign;
- keyword;
- domain;
- source;
- browser;
- device;
- city;
- brand;
- model;
- class.

### Курсы валют
Для расчёта стоимости автомобилей в рублях используются
официальные курсы Центрального банка РФ.

Архитектура:
```text
CBR
 ↓
Python
 ↓
raw.currency_rates
 ↓
dbt
 ↓
marts
```

Исторические курсы загружаются отдельным скриптом:
```python
python scripts/backfill_currency_rates.py
```

Актуальный курс обновляется ежедневно через Airflow.

#### Airflow
Airflow используется для автоматизации регулярного обновления данных.

Текущий DAG:
```text
update_currency_rates
        ↓
     dbt build
```

DAG:
``` python
airflow/dags/auto_dealer_dag.py
```
Airflow запускается в Docker.

После запуска:
```text
http://localhost:8081
```

## Power BI

В проекте реализованы две аналитические страницы
и отдельная главная страница навигации.

### 1. Отчёт по продажам

**Цель**: понять, сколько автомобилей продано,
на какую сумму и сколько маржинальной прибыли сформировано.

**Основные показатели:**
- продажи;
- средняя стоимость автомобиля;
- количество моделей;
- продажи в день;
- маржинальная прибыль;
- маржинальность;
- Contribution Margin.

**Отчёт позволяет анализировать показатели:**
- по периоду;
- городу;
- автомобилю.

Также реализовано переключение между режимами
анализа продаж и Contribution Margin.

### 2. Эффективность интернет-рекламы

Цель: понять, откуда приходит трафик,
как пользователи проходят воронку и какие источники
формируют продажи и маржинальную прибыль.

Основные этапы воронки:
```text
Sessions
   ↓
Conversions
   ↓
Dealer meetings
   ↓
Estimates
   ↓
Sales
```

Основные показатели:
- расходы на рекламу;
- прибыль на 1 ₽ рекламы;
- количество сессий;
- конверсии;
- продажи;
- маржинальная прибыль;
- ROMI.

Для анализа можно менять гранулярность:
- medium;
- campaign;
- keyword;
- domain;
- source;
- device;
- browser;
- city;
- brand;
- class;
- model;
- pageviews.

## Результат

В результате проекта построен end-to-end pipeline:
```text
Source data
    ↓
Python ingestion
    ↓
PostgreSQL raw
    ↓
dbt staging
    ↓
dbt marts
    ↓
Power BI
```

Решение позволяет анализировать:
- продажи;
- стоимость автомобилей;
- маржинальную прибыль;
- contribution margin;
- рекламные расходы;
- конверсию;
- воронку продаж;
- эффективность рекламных каналов.

## Особенности исходных данных

Исходный набор данных является тестовым и содержит
обезличенные данные.

Для части исходных данных потребовалось восстановить
аналитически необходимые значения и обеспечить согласованность
между CRM, GA и справочниками.

Отдельное внимание уделено:
- сопоставлению CRM и GA;
- датам продаж и сессий;
- истории цен автомобилей;
- валютам;
- рекламным расходам;
- согласованности справочников.

Поэтому проект демонстрирует не только построение BI,
но и работу с неполными и неоднородными исходными данными.

## Запуск проекта

1. Клонирование
```bash
git clone <repository-url>
cd car-dealer
```

2. Настройка окружения
Создать .env на основе:
```text
.env.example
```

3. Запуск Docker
```bash
docker compose up -d --build
```

4. Загрузка данных
Поместить исходные файлы в:
```text
data/
```

После этого запустить:
```bash
python -m ingestion.main
```

5. Проверка dbt
```bash
docker exec airflow_autodealer \
  dbt debug \
  --project-dir /opt/airflow/project/dbt_project \
  --profiles-dir /opt/airflow/project/dbt_project
```

6. Сборка dbt
```bash
docker exec airflow_autodealer \
  dbt build \
  --project-dir /opt/airflow/project/dbt_project \
  --profiles-dir /opt/airflow/project/dbt_project
```

7. Airflow
```text
http://localhost:8081
```

## Что планируется развивать
ClickHouse как аналитический serving layer;
Apache Superset.