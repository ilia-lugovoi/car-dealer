with calc_price_rub as (
    select
        se.id,
        se.client_id,
        se.sale_date,
        se.sale_city,
        se.model_id,
        se.session_id,
        se.model_name,
        se.brand_name,
        se.class_name,
        se.sales_medium,
        se.price_original,
        se.margin_pct,
        se.currency_code,
        se.ad_cost,
        case
            when se.currency_code = 'RUB' then se.price_original
            else se.price_original * se.rate_value / nullif(se.nominal, 0)
        end as price_rub
    from {{ ref('int_sales_enriched') }} se
),
calc_gp_cm as (
    select
        cpr.*,
        cpr.price_rub * (1 - cpr.margin_pct) as gross_profit_rub,
        (cpr.price_rub * (1 - cpr.margin_pct)) - cpr.ad_cost as contribution_margin_rub
    from calc_price_rub cpr
),
calc_ad_ref as (
    select
        cgc.*,
        case
            when sales_medium = 'referral' THEN contribution_margin_rub * 0.05
            ELSE 0
        end as ad_cost_sale_referral 
    from calc_gp_cm cgc
)

select
    caf.*,
    caf.ad_cost + caf.ad_cost_sale_referral as final_ad_cost,
    caf.contribution_margin_rub - caf.ad_cost_sale_referral as final_contribution_margin_rub 
from calc_ad_ref caf