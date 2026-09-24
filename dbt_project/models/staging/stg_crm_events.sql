SELECT
    id::int as id,
    client_id::int as client_id,
    ga_session_id::int as ga_session_id,
    count_cost::int as count_cost,
    dealer_meet::int as dealer_meet,
    crm_sale::int as crm_sale,
    sale_city::text as sale_city,
    saled_model_id::int as saled_model_id,
    sale_date::date as sale_date
FROM {{ source('raw', 'crm_events') }}