select
    id as session_id,
    client_id,
    date as session_date,
    ad_cost,
    medium,
    row_number() over (
        partition by client_id, date
        order by id
    ) as sale_rn
from {{ ref('stg_ga_sessions') }}
where sale = 1
