select
    s.id,
    s.client_id,
    s.sale_date,
    s.sale_city,
    s.model_id,
    s.session_id,
    s.ad_cost,
    s.sales_medium,
    m.model_name,
    m.brand_name,
    m.class_name,
    m.price_original,
    m.margin_pct,
    m.currency_code,
    cr.nominal,
    cr.rate_value
from {{ ref('int_sales_with_session') }} s
left join {{ ref('int_models_with_currency') }} m
    on s.model_id = m.id
left join {{ ref('stg_currency_rates') }} cr
    on m.currency_code = cr.currency_code
   and s.sale_date = cr.rate_date
