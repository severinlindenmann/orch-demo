-- Daily consumption per meter, for the ops dashboard.
select
    meter_id,
    date_trunc('day', read_at) as read_date,
    sum(kwh)                   as total_kwh,
    sum(case when is_suspect then 1 else 0 end) as suspect_intervals
from {{ ref('fct_meter_reads') }}
group by 1, 2
