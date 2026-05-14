select
    s.id,
    s.client_id,
    s.sale_date,
    s.sale_city,
    s.model_id,
    gs.session_id,
    gs.ad_cost,
    gs.medium as sales_medium
from {{ ref('int_sales_ranked') }} s
left join {{ ref('int_ga_sales_ranked') }} gs
    on s.client_id = gs.client_id
   and s.sale_date = gs.session_date
   and s.sale_rn = gs.sale_rn
