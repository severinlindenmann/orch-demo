---
id: DEMO-0010
title: Flag duplicate interval reads in the quality gate
type: feature
priority: normal
size: s
status: open
created: 2026-10-02T07:43Z
updated: 2026-10-02T07:47Z
external:
- key: '14'
  url: https://github.com/severinlindenmann/orch-demo/issues/14
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
    hash: sha256:6807b9fb2110cd9bc6b133f507964aebcfcab4449ea0233077c1c99cac04d4de
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

# DEMO-0010 — Flag duplicate interval reads in the quality gate

## Ask

## Context

## Requirements

- Duplicate (meter_id, read_at) rows above zero must fail the quality gate by default.
- The failure message must include the duplicate count and an example key.

## Acceptance criteria

- [ ] QualityReport.passed() fails when duplicate_rows > 0
- [ ] Failure message includes count and an example (meter_id, read_at)
- [ ] Existing passing-run tests still pass unchanged

## Out of scope

- Automatic de-duplication at ingest time (handled separately by dedupe_reads).

## Proposal

## Plan

## Current state

## Verification

## Decisions

## Log

- 2026-10-02T07:43Z [claude-code cc8b] created
- 2026-10-02T07:47Z [claude-code cc8b] updated Requirements
- 2026-10-02T07:47Z [claude-code cc8b] updated Acceptance criteria
- 2026-10-02T07:47Z [claude-code cc8b] updated Out of scope
- 2026-10-02T07:47Z [you] approved requirements → open

## Findings
