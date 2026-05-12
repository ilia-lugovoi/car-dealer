SELECT
	m.id,
	m.model_name,
	m.price_original,
	m.margin_pct,
    m.currency_id,
	c.currency_code
FROM {{ ref('stg_models') }} m
JOIN {{ ref('stg_currencies') }} c ON m.currency_id = c.id
