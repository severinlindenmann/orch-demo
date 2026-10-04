## Requirements

- mart_daily_consumption must be partitioned by month on read_date.
- Rebuilds must only touch the current and previous partition, not the full history.

## Acceptance criteria

- [ ] Table partitioned by month
- [ ] Incremental rebuild logic limited to current + previous partition
- [ ] Documented in sql/marts/

## Out of scope

- Partitioning fct_meter_reads itself (separate ticket if needed later).
