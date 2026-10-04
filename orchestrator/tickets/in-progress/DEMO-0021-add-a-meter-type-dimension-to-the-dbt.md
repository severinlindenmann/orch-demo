---
id: DEMO-0021
title: Add a meter_type dimension to the dbt marts
type: feature
priority: normal
size: m
status: in-progress
created: 2026-10-02T08:03Z
updated: 2026-10-04T14:21Z
external:
- key: GH-30
  url: https://github.com/severinlindenmann/orch-demo/issues/30
repos:
- dbt
branches:
  dbt: feature/DEMO-0021-meter-type-dim
worktrees: {}
prs:
- repo: dbt
  url: https://github.com/severinlindenmann/orch-demo-dbt/pull/1
  state: draft
parent: null
sprint: S1
blocked_by: []
follow_ups: []
labels: []
gates:
  requirements:
    approved: 2026-10-04T03:06Z
    via: tty
    hash: sha256:92ce26f1d891e027467d02ea52e86e759d594c27e81fe1f2d537044f8d782aff
    hash_v: 3
  plan:
    approved: 2026-10-04T03:14Z
    via: tty
    hash: sha256:ab1e8d9d148df5cfd0eb81329cf3464dea4865640beeb9b11fd14be72a26436b
    hash_v: 3
  verify:
    verdict: null
    at: null
    via: null
questions: []
claim:
  session: 9cca04e5-da2c-583a-8b76-451980e1de33
  harness: claude-code
  at: 2026-10-04T14:21Z
sessions:
- id: 9cca04e5-da2c-583a-8b76-451980e1de33
  harness: claude-code
  model: null
  started: 2026-10-04T03:08Z
---

# DEMO-0021 — Add a meter_type dimension to the dbt marts

## Requirements

- Add dim_meter_type and join it in fct_meter_reads.

## Acceptance criteria

- [ ] dim_meter_type builds
- [ ] fct_meter_reads joins it
- [ ] The SQL lint stays green

## Plan

1. Write dim_meter_type.
2. Join it in fct_meter_reads.
3. Drop meter_type from stg_meters.

## Tasks

- [/] T1 Write dim_meter_type
  - ref: file:dbt/models/marts/fct_meter_reads.sql
- [ ] T2 Join dim_meter_type in fct_meter_reads
  - needs: T1
- [-] T3 Drop meter_type from stg_meters
  - why: stg_meters keeps meter_type until DEMO-0023 ships

## Log

- 2026-10-02T08:03Z [claude-code 9cca] created
- 2026-10-04T03:04Z [claude-code 9cca] updated Requirements
- 2026-10-04T03:04Z [claude-code 9cca] updated Acceptance criteria
- 2026-10-04T03:06Z [you] approved requirements → open
- 2026-10-04T03:08Z [claude-code 9cca] claimed (open → in-progress)
- 2026-10-04T03:10Z [claude-code 9cca] updated Plan
- 2026-10-04T03:12Z [claude-code 9cca] added T1, T2, T3
- 2026-10-04T03:14Z [you] approved plan
- 2026-10-04T03:16Z [claude-code 9cca] started T1
- 2026-10-04T03:18Z [claude-code 9cca] skipped T3: stg_meters keeps meter_type until DEMO-0023 ships
- 2026-10-04T03:20Z [claude-code 9cca] linked branch feature/DEMO-0021-meter-type-dim, pr https://github.com/severinlindenmann/orch-demo-dbt/pull/1
- 2026-10-04T03:22Z [claude-code 9cca] The SQL lint fails: dim_meter_type still uses select *.
- 2026-10-04T11:06Z [claude-code 9cca] linked sprint S1
- 2026-10-04T14:21Z [claude-code 9cca] claimed
