SELECT
	rate_date::date as rate_date,
	currency_code::text as currency_code,
	nominal::int as nominal,
	rate_value::int as rate_value,
	update_timestamp::timestamp as update_timestamp
FROM {{ source('raw', 'currency_rates') }}