with sales as (
    select
        s.*,
        row_number() over (
            partition by s.client_id, s.sale_date
            order by s.id
        ) as sale_rn
    from {{ ref('stg_sales') }} s
),
ga_sales as (
    select
        id as session_id,
        client_id,
        [date] as session_date,
        ad_cost,
        row_number() over (
            partition by client_id, [date]
            order by id
        ) as sale_rn
    from {{ ref('stg_ga_sessions') }}
    where sale = 1
),
sales_with_session as (
    select
        s.id,
        s.client_id,
        s.sale_date,
        s.sale_city,
        s.model_id,
        gs.session_id,
        gs.ad_cost
    from sales s
    left join ga_sales gs
        on s.client_id = gs.client_id
       and s.sale_date = gs.session_date
       and s.sale_rn = gs.sale_rn
)
select
    s.id,
    s.client_id,
    s.sale_date,
    s.sale_city,
    s.model_id,
    s.session_id,
    m.model_name,
    m.price_original,
    m.margin_pct,
    m.currency_code,
    s.ad_cost,
    case
        when m.currency_code = 'RUB' then m.price_original
        else m.price_original * cr.rate_value / nullif(cr.nominal, 0)
    end as price_rub,
    case
        when m.currency_code = 'RUB' then m.price_original * m.margin_pct
        else (m.price_original * cr.rate_value / nullif(cr.nominal, 0)) * m.margin_pct
    end as gross_profit_rub,
    case
        when m.currency_code = 'RUB' and m.price_original <> 0 then s.ad_cost / m.price_original
        when m.currency_code <> 'RUB' and (m.price_original * cr.rate_value / nullif(cr.nominal, 0)) <> 0
            then s.ad_cost / (m.price_original * cr.rate_value / nullif(cr.nominal, 0))
    end as ad_spend_share
from sales_with_session s
left join {{ ref('int_models_with_currency') }} m
    on s.model_id = m.id
left join {{ ref('stg_currency_rates') }} cr
    on m.currency_code = cr.currency_code
   and s.sale_date = cr.rate_date
