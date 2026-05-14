SELECT
	CAST(id as int) as id,
	model_name,
	CAST(price_original as decimal(18, 6)) as price_original,
	CAST(margin_pct as decimal(18, 6)) as margin_pct,
	CAST(brand_id as int) as brand_id,
	CAST(class_id as int) as class_id,
	CAST(currency_id as int) as currency_id
FROM {{ source('raw', 'models') }}
