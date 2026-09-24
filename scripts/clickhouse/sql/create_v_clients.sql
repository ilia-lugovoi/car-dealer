CREATE TABLE IF NOT EXISTS v_clients
(
    client_id String,
    sessions_cnt Nullable(Int32),
    total_pageviews Nullable(Int32),
    total_conversions Nullable(Int32),
    total_ad_cost Nullable(Decimal(18, 2)),
    first_session_date Nullable(String),
    last_session_date Nullable(String),
    sales_cnt Nullable(Int32),
    total_price_rub Nullable(Decimal(18, 2)),
    total_gross_profit_rub Nullable(Decimal(18, 2)),
    total_contribution_margin_rub Nullable(Decimal(18, 2)),
    last_sale_date Nullable(String)
)
ENGINE = MergeTree
ORDER BY client_id;
