SELECT
    CAST(id as int) as id,
    medium_group_name,
    CAST(medium_group_sort as int) as medium_group_sort
FROM {{ source('raw', 'medium_groups') }}
