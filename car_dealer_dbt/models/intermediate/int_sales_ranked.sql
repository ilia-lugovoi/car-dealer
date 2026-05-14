select
    *,
    row_number() over (
        partition by client_id, sale_date
        order by id
    ) as sale_rn
from {{ ref('stg_sales') }}
