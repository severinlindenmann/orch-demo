---
id: DEMO-0012
title: Partition mart_daily_consumption by month
type: feature
priority: normal
size: l
status: open
created: 2026-10-02T07:43Z
updated: 2026-10-02T07:48Z
external:
- key: GH-6
  url: https://github.com/severinlindenmann/orch-demo/issues/6
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
    approved: 2026-10-02T07:47Z
    via: tty
    hash: sha256:4ae5826b2a6194d2391eb2726854cb73832f8e56eba60ff66a8b352ba7880e22
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

# DEMO-0012 — Partition mart_daily_consumption by month

## Requirements

- mart_daily_consumption must be partitioned by month on read_date.
- Rebuilds must only touch the current and previous partition, not the full history.

## Acceptance criteria

- [ ] Table partitioned by month
- [ ] Incremental rebuild logic limited to current + previous partition
- [ ] Documented in sql/marts/

## Out of scope

- Partitioning fct_meter_reads itself (separate ticket if needed later).

## Log

- 2026-10-02T07:43Z [claude-code cc8b] created
- 2026-10-02T07:47Z [claude-code cc8b] updated Requirements
- 2026-10-02T07:47Z [claude-code cc8b] updated Acceptance criteria
- 2026-10-02T07:47Z [claude-code cc8b] updated Out of scope
- 2026-10-02T07:47Z [you] approved requirements → open
- 2026-10-04T14:20Z [you] adopted the unsigned gate requirements into the ledger
- 2026-10-02T07:48Z [you] edited the ticket file
