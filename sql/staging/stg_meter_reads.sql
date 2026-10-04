-- Staging model: one row per raw gateway interval read, lightly typed.
select
    meter_id,
    gateway_id,
    cast(read_at as timestamp) as read_at,
    cast(kwh as double)        as kwh
from {{ source('gateway_exports', 'raw_meter_reads') }}
