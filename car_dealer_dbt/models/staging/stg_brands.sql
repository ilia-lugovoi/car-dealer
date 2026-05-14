SELECT
    CAST(id as int) as id,
    brand_name
FROM {{ source('raw', 'brands') }}
