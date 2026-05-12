with ga_agg as (
    select
        client_id,
        count(*) as sessions_cnt,
        sum(pageviews) as total_pageviews,
        sum(conversion) as total_conversions,
        sum(ad_cost) as total_ad_cost,
        min([date]) as first_session_date,
        max([date]) as last_session_date
    from {{ ref('stg_ga_sessions') }}
    group by client_id
),
sales_agg as (
    select
        client_id,
        count(*) as sales_cnt,
        sum(price_rub) as total_price_rub,
        sum(gross_profit_rub) as total_gross_profit_rub,
        max(sale_date) as last_sale_date
    from {{ ref('int_sales') }}
    group by client_id
)
select
    c.client_id,
    c.client_name,
    c.phone,
    c.city,
    ga.sessions_cnt,
    ga.total_pageviews,
    ga.total_conversions,
    ga.total_ad_cost,
    ga.first_session_date,
    ga.last_session_date,
    sa.sales_cnt,
    sa.total_price_rub,
    sa.total_gross_profit_rub,
    sa.last_sale_date
from {{ ref('stg_clients') }} c
left join ga_agg ga
    on c.client_id = ga.client_id
left join sales_agg sa
    on c.client_id = sa.client_id
