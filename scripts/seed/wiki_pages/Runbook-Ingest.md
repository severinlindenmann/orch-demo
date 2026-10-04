---
title: "Runbook: ingest"
documents:
  - ingest:src/acme_ingest/download.py
  - ingest:config/gateways.json
---

# Runbook: ingest

**Retries.** The downloader backs off 2, 4, 8, 16, 32 s and gives up after five attempts. A `Retry-After` header wins (see [download.py](https://github.com/severinlindenmann/orch-demo-ingest/blob/main/src/acme_ingest/download.py)). HTTP 429 without the header is DEMO-0020.

**Empty exports.** An empty file returns no rows and logs a warning (DEMO-0027).

**Failed runs on int.** Open the Databricks page, check run 9001 of acme-ingest-daily and follow DEMO-0016. Older timezone issues: GH-11.

<!-- seeded by orch-demo/scripts/seed/wiki_pages; edit the source there -->
