SELECT
	CAST(id as int) as id,
	client_id,
	CAST(sale_date as date) as sale_date,
	sale_city,
	CAST(model_id as int) as model_id
FROM {{ source('raw', 'sales') }}
