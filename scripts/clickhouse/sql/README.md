# ClickHouse scripts

В этой папке лежат DDL-скрипты для витрин ClickHouse:

- `create_v_medium.sql`
- `create_v_clients.sql`
- `create_v_sessions.sql`

Базовый сценарий загрузки данных:

1. Создать таблицу в `clickhouse-client` через один из `CREATE TABLE`-скриптов.
2. Выгрузить соответствующую view из MS SQL в CSV.
3. Скопировать CSV в контейнер:

```powershell
docker cp "C:\path\to\file.csv" clickhouse_autodealer:/tmp/file.csv
```

4. Выполнить импорт внутри контейнера:

```sh
clickhouse-client \
  --user analytics \
  --password analytics \
  --database car_dealer \
  --format_csv_null_representation='NULL' \
  --query="INSERT INTO table_name FORMAT CSV" < /tmp/file.csv
```

Для широкой витрины `v_sessions` лучше использовать CSV с разделителем `;`:

```sh
clickhouse-client \
  --user analytics \
  --password analytics \
  --database car_dealer \
  --format_csv_delimiter=';' \
  --format_csv_null_representation='NULL' \
  --query="INSERT INTO v_sessions FORMAT CSV" < /tmp/v_sessions_sc.csv
```

Если витрина перезагружается полностью, перед повторным импортом лучше делать:

```sql
TRUNCATE TABLE table_name;
```
