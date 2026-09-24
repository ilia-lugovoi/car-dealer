SELECT
    id::int as id,
    client_city::text as client_city
FROM {{ source('raw', 'clients') }}