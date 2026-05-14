SELECT
	m.id,
	m.model_name,
	m.price_original,
	m.margin_pct,
    m.brand_id,
    b.brand_name,
    m.class_id,
    cl.class_name,
    m.currency_id,
	c.currency_code
FROM {{ ref('stg_models') }} m
JOIN {{ ref('stg_brands') }} b ON m.brand_id = b.id
JOIN {{ ref('stg_classes') }} cl ON m.class_id = cl.id
JOIN {{ ref('stg_currencies') }} c ON m.currency_id = c.id
