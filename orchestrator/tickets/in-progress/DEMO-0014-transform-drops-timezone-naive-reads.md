---
id: DEMO-0014
title: Transform drops timezone-naive reads instead of assuming UTC
type: bug
priority: high
size: s
status: in-progress
created: 2026-10-02T07:43Z
updated: 2026-10-02T07:47Z
external:
- key: '11'
  url: https://github.com/severinlindenmann/orch-demo/issues/11
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
    hash: sha256:ae5e91e4a0605f9c7366a1247efb49e3867262728cc67a9a1f5c5ae023428425
  plan:
    approved: 2026-10-02T07:47Z
    via: tty
    hash: sha256:345b0222d03ca8d0a14714c6adf477a9051575fcd9e539f2e5e5dc3558737ed7
  verify:
    verdict: null
    at: null
    via: null
questions: []
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

# DEMO-0014 — Transform drops timezone-naive reads instead of assuming UTC

## Ask

## Context

## Requirements

- A timezone-naive read_at must be treated as UTC instead of raising a validation error.
- Each time this happens must be logged so the firmware issue can be chased.

## Acceptance criteria

- [ ] A naive timestamp is accepted and treated as UTC
- [ ] A warning is logged when a naive timestamp is coerced
- [ ] Regression test with a naive timestamp input

## Out of scope

- Fixing the GW-09 firmware itself (tracked separately with the vendor).

## Proposal

## Plan

1. In _parse_timestamp / RawMeterRead construction, detect a naive datetime.
2. Attach UTC and log a warning with the gateway id.
3. Regression test for a naive-timestamp row.

## Current state

## Verification

## Decisions

## Log

- 2026-10-02T07:43Z [claude-code cc8b] created
- 2026-10-02T07:47Z [claude-code cc8b] updated Requirements
- 2026-10-02T07:47Z [claude-code cc8b] updated Acceptance criteria
- 2026-10-02T07:47Z [claude-code cc8b] updated Out of scope
- 2026-10-02T07:47Z [claude-code cc8b] updated Plan
- 2026-10-02T07:47Z [you] approved requirements → open
- 2026-10-02T07:47Z [claude-code cc8b] claimed (open → in-progress)
- 2026-10-02T07:47Z [you] approved plan
- 2026-10-02T07:47Z [claude-code cc8b] Implementing the UTC coercion now; no branch pushed yet.

## Findings
