-- Staging model: meter master data (one row per physical meter).
select
    meter_id,
    substation_id,
    install_date,
    meter_type
from {{ source('asset_registry', 'meters') }}
