SELECT
    medium_name::text as medium_name,
    medium_group_id::int as medium_group_id,
    medium_sort::int as medium_sort
FROM {{ source('raw', 'mediums') }}