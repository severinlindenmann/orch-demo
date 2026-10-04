---
title: Architecture overview
documents:
  - acme-energy-data:src/acme/**
  - ingest:src/acme_ingest/**
  - dbt:models/**
---

# Architecture overview

Gateway exports flow through three repos:

1. **acme-ingest** downloads the exports. DEMO-0019 moves the download here from acme-energy-data.
2. **acme-energy-data** transforms and checks them (`src/acme/transform.py`, `src/acme/quality.py`); DEMO-0014 fixed timezone-naive reads.
3. **acme-dbt** builds the marts; DEMO-0021 adds the meter_type dimension.

Jobs and environments are defined in acme-infra. See [Runbook: ingest](Runbook-Ingest) and [Data model](Data-Model).

<!-- seeded by orch-demo/scripts/seed/wiki_pages; edit the source there -->
