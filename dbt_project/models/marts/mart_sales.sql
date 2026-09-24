with sales as (
    select
        id as sale_id,
        sale_date as date,
        sale_city as city,
        saled_model_id as model_id,
        ga_session_id
    from {{ ref('stg_crm_events') }}
    where crm_sale = 1
),
price_history as (
    select
        s.sale_id,
        s.date,
        s.city,
        s.model_id,
        s.ga_session_id,
        p.price_original,
        p.margin_pct,
        p.currency_code,
        p.effective_date,
        row_number() over(
            partition by s.sale_id
            order by p.effective_date desc
        ) as rn
    from sales s
    left join {{ ref('stg_prices') }} p
        on s.model_id = p.model_id
        and s.date >= p.effective_date
),
full_data as (
    select
        ph.sale_id,
        ph.date,
        ph.city,
        ph.model_id,
        ph.ga_session_id,
        ph.price_original,
        ph.margin_pct,
        ph.currency_code,
        cur.rate_value,
        cur.nominal,
        ga.ad_cost,
        ga.medium,
        m.model_name,
        b.brand_name,
        c.class_name
    from price_history ph
    left join {{ ref('stg_currency_rates') }} cur
        on ph.currency_code = cur.currency_code
        and ph.date = cur.rate_date
    left join {{ ref('stg_ga_sessions') }} ga
        on ph.ga_session_id = ga.id
    left join {{ ref('stg_models') }} m
        on ph.model_id = m.id
    left join {{ ref('stg_brands') }} b
        on m.brand_id = b.id
    left join {{ ref('stg_classes') }} c
        on m.class_id = c.id
    where ph.rn = 1
),
calc_revenue_rub as (
    select
        sale_id,
        date,
        city,
        model_id,
        case
            when rate_value IS NULL then price_original
            else price_original * rate_value / nominal
        end as price_original_rub,
        margin_pct,
        ad_cost,
        medium,
        model_name,
        brand_name,
        class_name
    from full_data
),
calc_margin as (
    select
        sale_id,
        date,
        city,
        model_id,
        price_original_rub,
        price_original_rub * margin_pct as margin_rub,
        case
            when medium = 'referral' then price_original_rub * margin_pct * 0.05
            when ad_cost IS NULL then 0
            else ad_cost
        end as final_ad_cost,
        model_name,
        brand_name,
        class_name
    from calc_revenue_rub
)
select
    sale_id,
    date,
    city,
    model_id,
    price_original_rub,
    margin_rub,
    final_ad_cost,
    margin_rub - final_ad_cost as contribution_margin_rub,
    model_name,
    brand_name,
    class_name
from calc_margin