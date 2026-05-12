CREATE TABLE IF NOT EXISTS v_clients
(
    client_id String,
    client_name Nullable(String),
    phone Nullable(String),
    city Nullable(String),
    sessions_cnt Nullable(Int32),
    total_pageviews Nullable(Int32),
    total_conversions Nullable(Int32),
    total_ad_cost Nullable(Decimal(18, 2)),
    first_session_date Nullable(String),
    last_session_date Nullable(String),
    sales_cnt Nullable(Int32),
    total_price_rub Nullable(Decimal(18, 2)),
    total_gross_profit_rub Nullable(Decimal(18, 2)),
    last_sale_date Nullable(String)
)
ENGINE = MergeTree
ORDER BY client_id;
