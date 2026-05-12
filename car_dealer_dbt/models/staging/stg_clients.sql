SELECT
    CAST(client_id as varchar(100)) as client_id,
    client_name,
    phone,
    city
FROM {{ source('raw', 'clients') }}
