---
title: "Runbook: deploys"
documents:
  - infra:jobs/*.json
  - infra:envs/*.json
---

# Runbook: deploys

The demo never deploys: job and environment files in acme-infra are validated by CI only.

- Every job needs `tags.cost_center` (DEMO-0025).
- int gets its own target file (DEMO-0024).
- The ingest service job arrives with DEMO-0019.

<!-- seeded by orch-demo/scripts/seed/wiki_pages; edit the source there -->
