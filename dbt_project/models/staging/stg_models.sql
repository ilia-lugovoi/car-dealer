SELECT
	id::int as id,
	name::text as model_name,
	brand_id::int as brand_id,
	class_id::int as class_id
FROM {{ source('raw', 'models') }}