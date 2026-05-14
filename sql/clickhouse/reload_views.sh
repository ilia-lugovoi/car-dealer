#!/bin/sh
set -eu

clickhouse-client --user analytics --password analytics --database car_dealer --query="DROP TABLE IF EXISTS v_medium"
clickhouse-client --user analytics --password analytics --database car_dealer --query="DROP TABLE IF EXISTS v_clients"
clickhouse-client --user analytics --password analytics --database car_dealer --query="DROP TABLE IF EXISTS v_sessions"

clickhouse-client --user analytics --password analytics --database car_dealer < /tmp/create_v_medium.sql
clickhouse-client --user analytics --password analytics --database car_dealer < /tmp/create_v_clients.sql
clickhouse-client --user analytics --password analytics --database car_dealer < /tmp/create_v_sessions.sql

cat /tmp/v_medium.csv | clickhouse-client --user analytics --password analytics --database car_dealer --query="INSERT INTO v_medium FORMAT CSV"
cat /tmp/v_clients.csv | clickhouse-client --user analytics --password analytics --database car_dealer --format_csv_null_representation=NULL --query="INSERT INTO v_clients FORMAT CSV"
cat /tmp/v_sessions_sc.csv | clickhouse-client --user analytics --password analytics --database car_dealer --format_csv_delimiter=';' --format_csv_null_representation=NULL --query="INSERT INTO v_sessions FORMAT CSV"

clickhouse-client --user analytics --password analytics --database car_dealer --query="SELECT 'v_medium' AS table_name, count() AS rows FROM v_medium"
clickhouse-client --user analytics --password analytics --database car_dealer --query="SELECT 'v_clients' AS table_name, count() AS rows FROM v_clients"
clickhouse-client --user analytics --password analytics --database car_dealer --query="SELECT 'v_sessions' AS table_name, count() AS rows FROM v_sessions"
