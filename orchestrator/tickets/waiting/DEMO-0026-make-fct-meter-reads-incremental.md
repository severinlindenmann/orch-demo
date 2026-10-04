---
id: DEMO-0026
title: Make fct_meter_reads incremental
type: feature
priority: high
size: m
status: waiting
created: 2026-10-02T08:13Z
updated: 2026-10-03T16:46Z
external:
- key: GH-35
  url: https://github.com/severinlindenmann/orch-demo/issues/35
repos:
- dbt
branches:
  dbt: feature/DEMO-0026-incremental-reads
worktrees: {}
prs:
- repo: dbt
  url: https://github.com/severinlindenmann/orch-demo-dbt/pull/6
  state: draft
parent: null
blocked_by: []
follow_ups: []
labels: []
gates:
  requirements:
    approved: 2026-10-03T16:28Z
    via: tty
    hash: sha256:8410485c7eba3d55eee86e8583b4a496ba1cfe3778ef402ee943ed50afce33c2
    hash_v: 3
  plan:
    approved: 2026-10-03T16:36Z
    via: tty
    hash: sha256:e76b66abab564c0d3fd233e89c19fcf0a133215e402229701f9b511458b390da
    hash_v: 3
  verify:
    verdict: null
    at: null
    via: null
questions:
- id: Q1
  text: Backfill 2025 in one run or month by month?
  why: One run needs a large warehouse for about 2 h.
  type: single
  options:
  - key: A
    label: One run on a large warehouse
    cost: about CHF 40, 2 h
  - key: B
    label: Month by month
    cost: 12 runs over one day
  recommended: B
  blocking: true
  asked: 2026-10-03T16:46Z
  answer: null
  note: null
  answered: null
  via: null
claim:
  session: a17ee9cd-d0e0-5321-ae1b-92e7431d98d1
  harness: claude-code
  at: 2026-10-03T16:30Z
sessions:
- id: a17ee9cd-d0e0-5321-ae1b-92e7431d98d1
  harness: claude-code
  model: null
  started: 2026-10-03T16:30Z
---

# DEMO-0026 — Make fct_meter_reads incremental

## Requirements

- Build fct_meter_reads incrementally by read_at.
- Backfill 2025 once.

## Acceptance criteria

- [ ] A nightly run takes under 5 min
- [ ] 2025 is backfilled and matches the full build

## Plan

1. Add the incremental model.
2. Backfill 2025.
3. Switch the nightly job.

## Tasks

- [x] T1 Add the incremental model
  - ref: file:dbt/models/marts/fct_meter_reads.sql
  - note: lint green on feature/DEMO-0026-incremental-reads
- [!] T2 Backfill the 2025 partitions
  - why: waits for the answer to Q1
  - on: Q1
- [ ] T3 Grant the dbt job SELECT on raw.meter_reads
  - owner: human

## Log

- 2026-10-02T08:13Z [claude-code a17e] created
- 2026-10-03T16:26Z [claude-code a17e] updated Requirements
- 2026-10-03T16:26Z [claude-code a17e] updated Acceptance criteria
- 2026-10-03T16:28Z [you] approved requirements → open
- 2026-10-03T16:30Z [claude-code a17e] claimed (open → in-progress)
- 2026-10-03T16:32Z [claude-code a17e] updated Plan
- 2026-10-03T16:34Z [claude-code a17e] added T1, T2, T3
- 2026-10-03T16:36Z [you] approved plan
- 2026-10-03T16:38Z [claude-code a17e] started T1
- 2026-10-03T16:40Z [claude-code a17e] T1 done: lint green on feature/DEMO-0026-incremental-reads
- 2026-10-03T16:42Z [claude-code a17e] started T2
- 2026-10-03T16:44Z [claude-code a17e] linked branch feature/DEMO-0026-incremental-reads, pr https://github.com/severinlindenmann/orch-demo-dbt/pull/6
- 2026-10-03T16:46Z [claude-code a17e] asked Q1 → waiting · T2 blocked on Q1
