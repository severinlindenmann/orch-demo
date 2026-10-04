---
title: "ADR-001: dbt for the marts layer"
documents:
  - dbt:dbt_project.yml
---

# ADR-001: dbt for the marts layer

**Status:** accepted. **Context:** spike DEMO-0008 (issue GH-2) compared dbt and plain SQL.
**Decision:** marts move to dbt; staging SQL in acme-energy-data stays until the models are ported.

<!-- seeded by orch-demo/scripts/seed/wiki_pages; edit the source there -->
