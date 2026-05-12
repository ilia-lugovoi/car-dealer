select
    medium_name,
    medium_sort
from {{ ref('stg_mediums') }}
