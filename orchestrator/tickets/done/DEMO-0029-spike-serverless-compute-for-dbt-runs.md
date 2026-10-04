---
id: DEMO-0029
title: 'Spike: serverless compute for dbt runs'
type: spike
priority: low
size: s
status: done
created: 2026-10-02T08:19Z
updated: 2026-10-03T00:52Z
external:
- key: GH-38
  url: https://github.com/severinlindenmann/orch-demo/issues/38
repos: []
branches: {}
worktrees: {}
prs: []
parent: null
blocked_by: []
follow_ups:
- DEMO-0030
labels: []
gates:
  requirements:
    approved: 2026-10-03T00:32Z
    via: tty
    hash: sha256:7f39a0f52b465560692dc8d1d1c97904e042bb9c8f3484863136f5cdcbc1acbd
    hash_v: 3
  plan:
    approved: 2026-10-03T00:40Z
    via: tty
    hash: sha256:6731ffb005993048645a622db0a1794be9d039972438646456418b8d1da4bd5f
    hash_v: 3
  verify:
    verdict: done
    at: 2026-10-03T00:52Z
    via: tty
questions: []
claim:
  session: null
  harness: null
  at: null
sessions:
- id: 808bfffc-9d4b-51b2-9df3-98f15918c1a9
  harness: claude-code
  model: null
  started: 2026-10-03T00:34Z
artifacts:
- name: compute-comparison.csv
  kind: dataset
  sha256: a06b7c90c7a9ce4488fa78df12b3b7985981192224bfaf7ec6ef224d91fbe2d3
  size: 101
  added: 2026-10-03T00:48Z
  label: Cost and run time, 10 runs each
  task: T1
  ac: 1
---

# DEMO-0029 — Spike: serverless compute for dbt runs

## Requirements

- Compare serverless and classic compute for the nightly dbt run.

## Acceptance criteria

- [ ] Cost and run time for 10 runs each, in Findings
- [ ] A recommendation

## Plan

Run the nightly build 10 times on each compute type in dev and compare.

## Tasks

- [x] T1 Run 10 builds on each compute type and compare
  - note: numbers in Findings

## Verification

10 nightly builds per compute type in dev; cost and run time per run in Findings.

## Log

- 2026-10-02T08:19Z [claude-code 808b] created
- 2026-10-02T08:21Z [claude-code 7cdc] follow-up DEMO-0030 created
- 2026-10-03T00:30Z [claude-code 808b] updated Requirements
- 2026-10-03T00:30Z [claude-code 808b] updated Acceptance criteria
- 2026-10-03T00:32Z [you] approved requirements → open
- 2026-10-03T00:34Z [claude-code 808b] claimed (open → in-progress)
- 2026-10-03T00:36Z [claude-code 808b] updated Plan
- 2026-10-03T00:38Z [claude-code 808b] added T1
- 2026-10-03T00:40Z [you] approved plan
- 2026-10-03T00:42Z [claude-code 808b] started T1
- 2026-10-03T00:44Z [claude-code 808b] T1 done: numbers in Findings
- 2026-10-03T00:46Z [claude-code 808b] updated Findings
- 2026-10-03T00:46Z [claude-code 808b] updated Verification
- 2026-10-03T00:48Z [claude-code 808b] added artifact compute-comparison.csv (dataset) for T1 for AC1
- 2026-10-03T00:50Z [claude-code 808b] moved in-progress → testing
- 2026-10-03T00:52Z [you] verdict done

## Findings

Serverless is 18% cheaper for runs under 15 min; cold start adds about 40 s. Recommend serverless for the nightly run. The runbook needs the decision (DEMO-0030).
