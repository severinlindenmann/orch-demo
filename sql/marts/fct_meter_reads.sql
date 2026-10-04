-- Curated fact table: normalized, deduplicated interval reads.
with ranked as (
    select
        *,
        row_number() over (
            partition by meter_id, read_at
            order by read_at desc
        ) as rn
    from {{ ref('stg_meter_reads') }}
)

select
    meter_id,
    gateway_id,
    read_at,
    kwh,
    kwh > 50.0 as is_suspect
from ranked
where rn = 1
