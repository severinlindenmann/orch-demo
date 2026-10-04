---
id: DEMO-0016
title: Investigate failed acme-ingest-daily runs on int
type: investigation
priority: normal
size: m
status: backlog
created: 2026-10-02T07:53Z
updated: 2026-10-04T11:10Z
external:
- key: GH-25
  url: https://github.com/severinlindenmann/orch-demo/issues/25
repos: []
branches: {}
worktrees: {}
prs: []
parent: null
sprint: S2
blocked_by: []
follow_ups: []
labels: []
gates:
  requirements:
    approved: null
    via: null
    hash: null
  plan:
    approved: null
    via: null
    hash: null
  verify:
    verdict: null
    at: null
    via: null
questions:
- id: Q1
  text: Alert on the first failed run or only after two in a row?
  why: Decides whether the fix also changes the alert rule.
  type: single
  options:
  - key: A
    label: Alert on the first failure
    cost: more noise at night
  - key: B
    label: Alert after two failures in a row
    cost: one day later on real outages
  recommended: B
  blocking: false
  asked: 2026-10-02T13:54Z
  answer: null
  note: null
  answered: null
  via: null
claim:
  session: null
  harness: null
  at: null
sessions: []
---

# DEMO-0016 — Investigate failed acme-ingest-daily runs on int

## Context

Run 9001 of acme-ingest-daily failed on int (Databricks page, int · simulated). prod ran fine on the same day.

## Requirements

- Find the root cause of int run 9001.
- Say whether prod is exposed to the same failure.

## Acceptance criteria

- [ ] Root cause written to Findings with the evidence
- [ ] A decision: fix now or file a follow-up

## Log

- 2026-10-02T07:53Z [claude-code 96c5] created
- 2026-10-02T13:52Z [claude-code 96c5] updated Context
- 2026-10-02T13:52Z [claude-code 96c5] updated Requirements
- 2026-10-02T13:52Z [claude-code 96c5] updated Acceptance criteria
- 2026-10-02T13:54Z [claude-code 96c5] asked Q1
- 2026-10-04T11:10Z [claude-code 96c5] linked sprint S2
