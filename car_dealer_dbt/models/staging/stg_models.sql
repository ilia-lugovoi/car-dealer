SELECT
	CAST(id as int) as id,
	model_name,
	CAST(price_original as decimal(18, 6)) as price_original,
	CAST(margin_pct as decimal(18, 6)) as margin_pct,
	CAST(currency_id as int) as currency_id
FROM {{ source('raw', 'models') }}
