SELECT
	id::int as id,
	client_id::text as ga_client_id,
	domain::text as domain,
	city::text as city,
	region::text as region,
	browser::text as browser,
	device_category::text as device_category,
	date::date as date,
	pageviews::int as pageviews,
	campaign::text as campaign,
	keyword::text as keyword,
	medium::text as medium,
	source::text as source,
	sessions::int as sessions,
	conversion::int as conversion,
	ad_cost::decimal(18, 2) as ad_cost
FROM {{ source('raw', 'ga_sessions') }}