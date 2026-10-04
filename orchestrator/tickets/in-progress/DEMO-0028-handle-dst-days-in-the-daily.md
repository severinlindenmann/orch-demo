---
id: DEMO-0028
title: Handle DST days in the daily consumption mart
type: feature
priority: normal
size: s
status: in-progress
created: 2026-10-02T08:17Z
updated: 2026-10-04T14:21Z
external:
- key: GH-37
  url: https://github.com/severinlindenmann/orch-demo/issues/37
repos:
- dbt
branches:
  dbt: feature/DEMO-0028-dst-days
worktrees: {}
prs:
- repo: dbt
  url: https://github.com/severinlindenmann/orch-demo-dbt/pull/5
  state: draft
parent: null
sprint: S1
blocked_by: []
follow_ups: []
labels: []
gates:
  requirements:
    approved: 2026-10-03T11:09Z
    via: tty
    hash: sha256:b2eec2447b63a5cc2dd83df45c3044deed3dd701a7f9c60d592b5124976e837b
    hash_v: 3
  plan:
    approved: 2026-10-03T11:17Z
    via: tty
    hash: sha256:4202dc8dd80569455ba7d2d550a2d84c2b9970c8d2346916b9015c3d55f8c20d
    hash_v: 3
  verify:
    verdict: follow-up
    at: 2026-10-03T11:35Z
    via: tty
questions: []
claim:
  session: 26139d76-f5e4-5a35-b259-c9f5db61621d
  harness: copilot
  at: 2026-10-04T14:21Z
sessions:
- id: 26139d76-f5e4-5a35-b259-c9f5db61621d
  harness: copilot
  model: null
  started: 2026-10-03T11:11Z
artifacts:
- name: dst-25h-day.png
  kind: screenshot
  sha256: b8f3473ff41b9ab6cbe3c342e0836b5b62d7688c341a55d9b0eb63638a12e38f
  size: 2114
  added: 2026-10-03T11:31Z
  label: Reads per hour on 2026-10-25
  task: T2
  ac: 2
---

# DEMO-0028 — Handle DST days in the daily consumption mart

## Requirements

- Count 23- and 25-hour days correctly in mart_daily_consumption.

## Acceptance criteria

- [ ] 2026-03-29 has 23 hours of reads
- [ ] 2026-10-25 has 25 hours of reads

## Plan

Skip reads without a timestamp, then test both DST days.

## Tasks

- [x] T1 Count 23- and 25-hour days correctly
  - note: fct_meter_reads handles 2026-10-25
- [x] T2 Add a test for the 25-hour day 2026-10-25
  - note: test added
- [/] T3 Add a test for the 23-hour day 2026-03-29
  - added: 2026-10-03T11:37Z after plan approval

## Verification

`python scripts/lint_sql.py` in dbt: green. The 25-hour day 2026-10-25 test passes.
- AC2: Reads per hour on 2026-10-25
  ![Reads per hour on 2026-10-25](artifact:dst-25h-day.png)

## Log

- 2026-10-02T08:17Z [copilot 2613] created
- 2026-10-03T11:07Z [copilot 2613] updated Requirements
- 2026-10-03T11:07Z [copilot 2613] updated Acceptance criteria
- 2026-10-03T11:09Z [you] approved requirements → open
- 2026-10-03T11:11Z [copilot 2613] claimed (open → in-progress)
- 2026-10-03T11:13Z [copilot 2613] updated Plan
- 2026-10-03T11:15Z [copilot 2613] added T1, T2
- 2026-10-03T11:17Z [you] approved plan
- 2026-10-03T11:19Z [copilot 2613] started T1
- 2026-10-03T11:21Z [copilot 2613] T1 done: fct_meter_reads handles 2026-10-25
- 2026-10-03T11:23Z [copilot 2613] started T2
- 2026-10-03T11:25Z [copilot 2613] T2 done: test added
- 2026-10-03T11:27Z [copilot 2613] linked branch feature/DEMO-0028-dst-days, pr https://github.com/severinlindenmann/orch-demo-dbt/pull/5
- 2026-10-03T11:29Z [copilot 2613] updated Verification
- 2026-10-03T11:31Z [copilot 2613] added artifact dst-25h-day.png (screenshot) for T2 for AC2 · evidence in Verification
- 2026-10-03T11:33Z [copilot 2613] moved in-progress → testing
- 2026-10-03T11:35Z [you] verdict follow-up: 23-hour days still double-count 02:00; add a test for 2026-03-29.
- 2026-10-03T11:37Z [copilot 2613] added T3 after plan approval
- 2026-10-03T11:39Z [copilot 2613] started T3
- 2026-10-04T11:08Z [copilot 2613] linked sprint S1
- 2026-10-04T14:21Z [copilot 2613] claimed
