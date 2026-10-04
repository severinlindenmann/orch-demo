---
id: DEMO-0015
title: Alert when suspect rate exceeds threshold for 3 consecutive runs
type: feature
priority: normal
size: m
status: waiting
created: 2026-10-02T07:43Z
updated: 2026-10-02T07:48Z
external:
- key: GH-12
  url: https://github.com/severinlindenmann/orch-demo/issues/12
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
    hash: sha256:48d59a26ba7216f827764c75d526ca844d6e79eed01833aa97b5318c568b723a
  plan:
    approved: 2026-10-02T07:47Z
    via: tty
    hash: sha256:8cf710806945c72701b1259c8e3f27b42e551e20dfd4acaf3627e7ed592a82ca
  verify:
    verdict: null
    at: null
    via: null
questions:
- id: Q1
  text: Where should the per-gateway suspect-streak state live between runs?
  why: The nightly job is stateless today; a streak counter needs to survive between runs.
  type: single
  options:
  - key: A
    label: In-memory within the nightly job process
    cost: lost on restart
  - key: B
    label: Persisted to a small state table in the warehouse
    cost: one migration
  - key: C
    label: Reuse the existing claims/session store
    cost: couples unrelated systems
  recommended: B
  blocking: true
  asked: 2026-10-02T07:47Z
  answer: null
  note: null
  answered: null
  via: null
claim:
  session: cc8be880-3610-520a-8cce-3b15f6753080
  harness: claude-code
  at: 2026-10-02T07:47Z
sessions:
- id: cc8be880-3610-520a-8cce-3b15f6753080
  harness: claude-code
  model: null
  started: 2026-10-02T07:47Z
---

# DEMO-0015 — Alert when suspect rate exceeds threshold for 3 consecutive runs

## Requirements

- Track suspect rate history per gateway across runs.
- Emit an alert after 3 consecutive breaches of the suspect-rate threshold for the same gateway.

## Acceptance criteria

- [ ] Per-gateway suspect-rate history is tracked across runs
- [ ] An alert (log line) fires after 3 consecutive breaches
- [ ] A single bad run, or breaches from different gateways, does not alert

## Out of scope

- Routing the alert anywhere beyond a log line (paging, Slack, etc.) — follow-up ticket.

## Plan

1. Decide where the per-gateway streak state lives (see open question).
2. Add a streak counter keyed by gateway_id, reset on a non-breaching run.
3. Emit a log-level alert when the streak reaches 3.
4. Unit test for the 3-strikes logic.

## Log

- 2026-10-02T07:43Z [claude-code cc8b] created
- 2026-10-02T07:47Z [claude-code cc8b] updated Requirements
- 2026-10-02T07:47Z [claude-code cc8b] updated Acceptance criteria
- 2026-10-02T07:47Z [claude-code cc8b] updated Out of scope
- 2026-10-02T07:47Z [claude-code cc8b] updated Plan
- 2026-10-02T07:47Z [you] approved requirements → open
- 2026-10-02T07:47Z [claude-code cc8b] claimed (open → in-progress)
- 2026-10-02T07:47Z [you] approved plan
- 2026-10-02T07:47Z [claude-code cc8b] asked Q1 → waiting
- 2026-10-04T14:21Z [you] adopted the unsigned gate requirements into the ledger
- 2026-10-04T14:21Z [you] adopted the unsigned gate plan into the ledger
- 2026-10-02T07:48Z [you] edited the ticket file
