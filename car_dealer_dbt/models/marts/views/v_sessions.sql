select
    sc.id,
    sc.client_id,
    sc.domain,
    sc.city,
    sc.region,
    sc.browser,
    sc.device_category,
    sc.[date],
    cast(sc.[date] as date) as date_dt,
    sc.pageviews,
    sc.campaign,
    sc.keyword,
    sc.medium,
    smg.medium_group_name as medium_group,
    sc.source,
    sc.sessions,
    sc.goal_completion_location,
    sc.conversion,
    sc.source_conv,
    sc.sale,
    coalesce(sc.model_ga_name, 'not found') as model_ga_name,
    sc.crm_city,
    sc.count_cost,
    sc.dealer_meet,
    sc.crm_sale,
    s.brand_name,
    s.class_name,
    coalesce(s.model_name, sc.model_ga_name, 'not found') as model_name,
    coalesce(s.price_original, 0) as price_original,
    s.currency_code,
    coalesce(s.final_ad_cost, sc.ad_cost) as ad_cost,
    coalesce(s.price_rub, 0) as price_rub,
    coalesce(s.gross_profit_rub, 0) as gross_profit_rub,
    coalesce(s.final_contribution_margin_rub, -sc.ad_cost) as contribution_margin_rub
from {{ ref('int_session_crm') }} sc
left join {{ ref('int_sales') }} s
    on sc.id = s.session_id
left join {{ ref('stg_mediums') }} sm
    on sc.medium = sm.medium_name
left join {{ ref('stg_medium_groups') }} smg
    on sm.medium_group_id = smg.id
