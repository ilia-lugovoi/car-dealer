with ga as (
    select
        *,
        row_number() over (
            partition by client_id, [date]
            order by id
        ) as client_date_rn
    from {{ ref('stg_ga_sessions') }}
),
crm as (
    select
        *,
        row_number() over (
            partition by client_id, event_date
            order by crm_sale desc, dealer_meet desc, count_cost desc, crm_city
        ) as client_date_rn
    from {{ ref('stg_crm_events') }}
)
select
    ga.*,
    crm.crm_city,
    crm.count_cost,
    crm.dealer_meet,
    crm.crm_sale
from ga
left join crm
    on ga.client_id = crm.client_id
   and ga.[date] = crm.event_date
   and ga.client_date_rn = crm.client_date_rn
