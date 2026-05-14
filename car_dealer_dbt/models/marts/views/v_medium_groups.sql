select
    medium_group_name,
    medium_group_sort
from {{ ref('stg_medium_groups') }}
