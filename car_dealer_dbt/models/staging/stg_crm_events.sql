SELECT
    CAST(client_id as varchar(100)) as client_id,
    crm_city,
    CAST(count_cost as int) as count_cost,
    CAST(dealer_meet as int) as dealer_meet,
    CAST(crm_sale as int) as crm_sale,
    CAST(event_date as date) as event_date
FROM {{ source('raw', 'crm_events') }}
