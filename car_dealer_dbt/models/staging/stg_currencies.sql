SELECT
	CAST(id as int) as id,
	CAST(currency_code as varchar(10)) as currency_code
FROM {{ source('raw', 'currencies') }}
