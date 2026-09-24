SELECT
    CAST(id as int) as id,
    class_name
FROM {{ source('raw', 'classes') }}
