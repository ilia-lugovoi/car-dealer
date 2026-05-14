select
    ga.*,
    crm.crm_city,
    crm.count_cost,
    crm.dealer_meet,
    crm.crm_sale
from {{ ref('stg_ga_sessions') }} ga
left join {{ ref('stg_crm_events') }} crm
    on ga.id = crm.ga_session_id
