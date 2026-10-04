---
id: DEMO-0035
title: Monthly tariff summary mart
type: feature
priority: normal
size: s
status: open
created: 2026-10-02T08:31Z
updated: 2026-10-04T11:14Z
external: []
repos: []
branches: {}
worktrees: {}
prs: []
parent: DEMO-0034
sprint: S2
blocked_by: []
follow_ups: []
labels: []
gates:
  requirements:
    approved: 2026-10-02T16:01Z
    via: tty
    hash: sha256:0738233ead2db42b9d474ef158b91cc49fe11fc764063fdc71590a9a5ba60407
    hash_v: 3
    epic: DEMO-0034
  plan:
    approved: 2026-10-02T16:01Z
    via: tty
    hash: sha256:832bea8230d4c74ef411b48ce09b5e11f4e056aaeef2d9737c75485fa55d9939
    hash_v: 3
    epic: DEMO-0034
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

# DEMO-0035 — Monthly tariff summary mart

## Requirements

- Build mart_tariff_monthly with consumption and cost per tariff and month.

## Acceptance criteria

- [ ] One row per tariff and month
- [ ] Cost matches the tariff table for October

## Plan

Join fct_meter_reads to the tariff seed and aggregate per month.

## Log

- 2026-10-02T08:31Z [claude-code 42c1] created in epic DEMO-0034
- 2026-10-02T14:56Z [claude-code 42c1] updated Requirements
- 2026-10-02T14:56Z [claude-code 42c1] updated Acceptance criteria
- 2026-10-02T14:56Z [claude-code 42c1] updated Plan
- 2026-10-02T16:01Z [you] approved with epic DEMO-0034: requirements and plan
- 2026-10-04T11:14Z [claude-code 42c1] linked sprint S2
