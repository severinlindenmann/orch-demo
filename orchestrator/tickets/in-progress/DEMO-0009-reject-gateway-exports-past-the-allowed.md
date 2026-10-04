---
id: DEMO-0009
title: Reject gateway exports past the allowed late window
type: feature
priority: normal
size: m
status: in-progress
created: 2026-10-02T07:43Z
updated: 2026-10-02T07:47Z
external:
- key: '9'
  url: https://github.com/severinlindenmann/orch-demo/issues/9
repos:
- acme-energy-data
branches:
  acme-energy-data: feature/DEMO-0009-late-arriving-exports
worktrees: {}
prs:
- repo: acme-energy-data
  url: https://github.com/severinlindenmann/orch-demo/pull/23
  state: draft
parent: null
blocked_by: []
follow_ups: []
labels: []
gates:
  requirements:
    approved: 2026-10-02T07:47Z
    via: tty
    hash: sha256:e9d9b5e22c1c98e5a9430f47993e35c24ee00b3f53d8d8258df035d9fe50291e
  plan:
    approved: 2026-10-02T07:47Z
    via: tty
    hash: sha256:80a5978521ee0627ba77f38e36c5dce02eb3cf27ee273c7e8255b8969a60f8f2
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

# DEMO-0009 — Reject gateway exports past the allowed late window

## Ask

## Context

## Requirements

- A gateway export older than allowed_late_days must be rejected with a clear error.
- A late-but-allowed export must be accepted and logged as late.

## Acceptance criteria

- [ ] check_export_age() returns False for on-time, True for late-but-allowed
- [ ] check_export_age() raises ExportTooLateError beyond allowed_late_days
- [ ] Tests cover on-time, late-but-allowed and rejected cases

## Out of scope

- Wiring the check into the nightly runner's main loop (follow-up ticket).

## Proposal

## Plan

1. Add ExportTooLateError and check_export_age(export_date, run_date, config).
2. age_days <= 0 -> on time; 0 < age_days <= allowed_late_days -> late but accepted (logged); beyond that -> raise.
3. Tests for all three cases.

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
- 2026-10-02T07:47Z [claude-code cc8b] linked branch feature/DEMO-0009-late-arriving-exports
- 2026-10-02T07:47Z [claude-code cc8b] linked pr https://github.com/severinlindenmann/orch-demo/pull/23
- 2026-10-02T07:47Z [claude-code cc8b] PR #23 open, CI green. Reviewer asked whether age_days should account for weekends/holidays rather than calendar days -- following up on that before this is ready to merge.

## Findings
