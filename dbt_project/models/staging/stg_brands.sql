SELECT
    id::int as id,
    brand_name::text as brand_name
FROM {{ source('raw', 'brands') }}