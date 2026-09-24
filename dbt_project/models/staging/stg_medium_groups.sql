SELECT
    id::int as id,
    medium_group_name::text as medium_group_name,
    medium_group_sort::int as medium_group_sort
FROM {{ source('raw', 'medium_groups') }}