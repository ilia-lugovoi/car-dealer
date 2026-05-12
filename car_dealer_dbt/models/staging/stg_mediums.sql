SELECT
    medium_name,
    CAST(medium_sort as int) as medium_sort,
    CAST(min_cost as decimal(18, 2)) as min_cost,
    CAST(max_cost as decimal(18, 2)) as max_cost,
    CAST(min_cost_sale as decimal(18, 2)) as min_cost_sale,
    CAST(max_cost_sale as decimal(18, 2)) as max_cost_sale,
    commentary
FROM {{ source('raw', 'mediums') }}
