SELECT
	CAST(rate_date as date) as rate_date,
	CAST(currency_code as varchar(10)) as currency_code,
	CAST(nominal as int) as nominal,
	CAST(rate_value as decimal(18, 6)) as rate_value,
	CAST(update_timestamp as datetime2) as update_timestamp
FROM {{ source('raw', 'currency_rates') }}
