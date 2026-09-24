SELECT
	id::int as id,
	model_id::int as model_id,
	effective_date::date as effective_date,
    price_original::decimal(18, 6) as price_original,
    margin_pct::decimal(18, 6) as margin_pct,
    currency_code::text as currency_code
FROM {{ source('raw', 'prices') }}