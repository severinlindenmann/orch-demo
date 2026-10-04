---
id: DEMO-0017
title: Load tariff tables as dbt seeds
type: feature
priority: high
size: m
status: backlog
created: 2026-10-02T07:55Z
updated: 2026-10-02T11:15Z
external:
- key: GH-26
  url: https://github.com/severinlindenmann/orch-demo/issues/26
repos: []
branches: {}
worktrees: {}
prs: []
parent: null
blocked_by: []
follow_ups: []
labels: []
gates:
  requirements:
    approved: null
    via: null
    hash: null
    changes_requested:
      at: 2026-10-02T11:15Z
      by: you
      message: Say which tariff years are in scope and who owns the CSV, then ask me again.
      hash: sha256:f6f1870370d7ceab2b4d024b0f34b78579a692461bf457776e2e36c70bdbdaf5
  plan:
    approved: null
    via: null
    hash: null
  verify:
    verdict: null
    at: null
    via: null
questions: []
claim:
  session: null
  harness: null
  at: null
sessions: []
---

# DEMO-0017 — Load tariff tables as dbt seeds

## Requirements

- Load the tariff tables as dbt seeds.
- Tariffs join to fct_meter_reads by tariff_code.

## Acceptance criteria

- [ ] seeds/tariffs.csv loads with dbt seed
- [ ] fct_meter_reads carries tariff_code

## Log

- 2026-10-02T07:55Z [claude-code 3cab] created
- 2026-10-02T11:13Z [claude-code 3cab] updated Requirements
- 2026-10-02T11:13Z [claude-code 3cab] updated Acceptance criteria
- 2026-10-02T11:15Z [you] asked for changes on the requirements: Say which tariff years are in scope and who owns the CSV, then ask me again.
