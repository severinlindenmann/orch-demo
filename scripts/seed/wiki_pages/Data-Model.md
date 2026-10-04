---
title: Data model
documents:
  - dbt:models/**
  - acme-energy-data:sql/**
---

# Data model

- `stg_meter_reads`, `stg_meters`: one row per read and per meter.
- `fct_meter_reads`: one row per meter and interval, joined to the meter type. DEMO-0026 makes it incremental; DEMO-0028 handles DST days.
- `dim_meter_type`: new in DEMO-0021, used by the threshold mart in DEMO-0022.
- `mart_daily_consumption`: partitioning by month is GH-6.

<!-- seeded by orch-demo/scripts/seed/wiki_pages; edit the source there -->
