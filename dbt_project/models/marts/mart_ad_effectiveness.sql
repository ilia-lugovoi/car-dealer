with ad_data as (
    select
        id,
        date,
        city,
        region,
        medium,
        campaign,
        keyword,
        domain,
        source,
        browser,
        device_category,
        sessions,
        conversion,
        pageviews,
        ad_cost
    from {{ ref('stg_ga_sessions') }}
    where date >= '2021-01-01'
        and date < '2021-06-01'
),
prep_data as (
    select
        ad.id,
        crm.client_id,
        ad.date as ga_date,
        crm.sale_date as sale_date,
        ad.city as ga_city,
        ad.region as ga_region,
        cl.client_city,
        crm.sale_city as sale_city,
        ad.sessions as sessions,
        ad.conversion as conversion,
        crm.count_cost as count_cost,
        crm.dealer_meet as dealer_meet,
        crm.crm_sale as sale,
        crm.id as sale_id,
        crm.saled_model_id,

        p.price_original,
        p.margin_pct,
        p.currency_code,
        p.effective_date,

        row_number() over(
            partition by ad.id
            order by p.effective_date desc
        ) as rn,

        ad.ad_cost,
        ad.pageviews,
        case
            when ad.sessions > 0 then ad.pageviews::numeric / ad.sessions
        end as pageviews_per_session,

        ad.medium,
        ad.campaign,
        ad.keyword,
        ad.domain,
        ad.source,
        ad.browser,
        ad.device_category
    from ad_data ad
    left join {{ ref('stg_crm_events') }} crm
        on ad.id = crm.ga_session_id
    left join {{ ref('stg_clients') }} cl
        on crm.client_id = cl.id
    left join {{ ref('stg_prices') }} p
        on crm.saled_model_id = p.model_id
        and crm.sale_date >= p.effective_date
),
full_data as (
    select
        pd.id,
        pd.ga_date,
        pd.sale_date,
        pd.ga_city,
        pd.ga_region,
        pd.client_city,
        pd.sale_city,
        pd.sessions,
        pd.conversion,
        pd.count_cost,
        pd.dealer_meet,
        pd.sale,
        pd.saled_model_id,
        case
            when cur.rate_value IS NULL then pd.price_original
            else pd.price_original * cur.rate_value / cur.nominal
        end as price_original_rub,
        pd.margin_pct,
        pd.ad_cost,
        pd.pageviews,
        pd.pageviews_per_session,
        pd.medium,
        pd.campaign,
        pd.keyword,
        pd.domain,
        pd.source,
        pd.browser,
        pd.device_category
    from prep_data pd
    left join {{ ref('stg_currency_rates') }} cur
        on pd.currency_code = cur.currency_code
        and pd.sale_date  = cur.rate_date
    where pd.rn = 1
),
last_calc as (
    select
        fd.id,
        fd.ga_date,
        fd.sale_date,
        fd.ga_city,
        fd.ga_region,
        fd.client_city,
        fd.sale_city,
        fd.sessions,
        fd.conversion,
        case
            when fd.count_cost IS NULL then 0
            else fd.count_cost
        end as count_cost,
        case
            when fd.dealer_meet IS NULL then 0
            else fd.dealer_meet
        end as dealer_meet,
        case
            when fd.sale IS NULL then 0
            else fd.sale
        end as sale,
        fd.saled_model_id,

        fd.price_original_rub,
        fd.price_original_rub * fd.margin_pct as margin_rub,
        case
            when fd.medium = 'referral' and fd.sale = 1 then fd.price_original_rub * fd.margin_pct * 0.05
            else fd.ad_cost
        end as final_ad_cost,

        fd.pageviews,
        fd.pageviews_per_session,
        case
            when fd.pageviews_per_session IS NULL then '0'
            when fd.pageviews_per_session < 1 then '0'
            when fd.pageviews_per_session < 5 then '1-4'
            when fd.pageviews_per_session < 11 then '5-10'
            when fd.pageviews_per_session < 21 then '11-20'
            else '21+'
        end as pageviews_per_session_group,

        fd.medium,
        fd.campaign,
        fd.keyword,
        fd.domain,
        fd.source,
        fd.browser,
        fd.device_category
    from full_data fd
)
select
    lc.id,
    lc.ga_date,
    lc.sale_date,
    lc.ga_city,
    lc.ga_region,
    lc.client_city,
    lc.sale_city,
    lc.sessions,
    lc.conversion,
    lc.count_cost,
    lc.dealer_meet,
    lc.sale,
    
    m.model_name,
    b.brand_name,
    c.class_name,

    lc.price_original_rub,
    lc.margin_rub,
    lc.final_ad_cost,
    lc.margin_rub - lc.final_ad_cost as contribution_margin_rub,

    lc.pageviews,
    lc.pageviews_per_session,
    lc.pageviews_per_session_group,

    lc.medium,
    md.medium_sort,
    mg.medium_group_name as medium_group,
    mg.medium_group_sort,
    lc.campaign,
    lc.keyword,
    lc.domain,
    lc.source,
    lc.browser,
    lc.device_category
from last_calc lc
left join {{ ref('stg_models') }} m
    on lc.saled_model_id = m.id
left join {{ ref('stg_brands') }} b
    on m.brand_id = b.id
left join {{ ref('stg_classes') }} c
    on m.class_id = c.id
left join {{ ref('stg_mediums') }} md
    on lc.medium = md.medium_name
left join {{ ref('stg_medium_groups') }} mg
    on md.medium_group_id = mg.id