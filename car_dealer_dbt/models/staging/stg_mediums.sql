SELECT
    medium_name,
    CAST(medium_group_id as int) as medium_group_id,
    CAST(medium_sort as int) as medium_sort
FROM {{ source('raw', 'mediums') }}
