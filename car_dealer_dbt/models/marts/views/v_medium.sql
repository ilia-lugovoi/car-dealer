select
    medium_name,
    medium_group_id,
    medium_sort
from {{ ref('stg_mediums') }}
