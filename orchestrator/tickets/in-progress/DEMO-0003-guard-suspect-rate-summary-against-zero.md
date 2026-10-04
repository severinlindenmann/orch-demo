---
id: DEMO-0003
title: Guard suspect-rate summary against zero rows
type: bug
priority: urgent
size: s
status: in-progress
created: 2026-10-02T07:43Z
updated: 2026-10-02T07:47Z
external:
- key: '5'
  url: https://github.com/severinlindenmann/orch-demo/issues/5
repos:
- acme-energy-data
branches:
  acme-energy-data: fix/DEMO-0003-quality-divide-by-zero
worktrees: {}
prs:
- repo: acme-energy-data
  url: https://github.com/severinlindenmann/orch-demo/pull/21
  state: draft
parent: null
blocked_by: []
follow_ups: []
labels: []
gates:
  requirements:
    approved: 2026-10-02T07:47Z
    via: tty
    hash: sha256:4568b2bf61a2b7e958eb25739a4016fc508f13145d77767f8c696e9b543e916b
  plan:
    approved: 2026-10-02T07:47Z
    via: tty
    hash: sha256:0d30ba65305174f88fcfb23e4236025034b9b40ca7c2e00c6667018d83f65d10
  verify:
    verdict: null
    at: null
    via: null
questions: []
claim:
  session: cc8be880-3610-520a-8cce-3b15f6753080
  harness: copilot
  at: 2026-10-02T07:47Z
sessions:
- id: cc8be880-3610-520a-8cce-3b15f6753080
  harness: copilot
  model: null
  started: 2026-10-02T07:47Z
---

# DEMO-0003 — Guard suspect-rate summary against zero rows

## Ask

## Context

## Requirements

- The on-call summary line must never raise ZeroDivisionError on an empty run.
- An empty run (no reads at all) must report a clean zero suspect rate.

## Acceptance criteria

- [ ] suspect_rate_percent() handles total_rows == 0 without raising
- [ ] Regression test for the empty-report case
- [ ] Normal non-empty case still computes the correct percentage

## Out of scope

- Reworking QualityReport's public API beyond this one summary helper.

## Proposal

## Plan

1. Add suspect_rate_percent(report) with an explicit zero-rows guard.
2. Regression test for total_rows == 0.
3. Regression test for the normal case to lock in the percentage math.

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
- 2026-10-02T07:47Z [copilot cc8b] claimed (open → in-progress)
- 2026-10-02T07:47Z [you] approved plan
- 2026-10-02T07:47Z [claude-code cc8b] linked branch fix/DEMO-0003-quality-divide-by-zero
- 2026-10-02T07:47Z [claude-code cc8b] linked pr https://github.com/severinlindenmann/orch-demo/pull/21
- 2026-10-02T07:47Z [copilot cc8b] PR #21 open. CI is red: tests/test_quality_zero_rows.py has one test with a wrong expected value, left in on purpose for this demo (see PR body). Fixing is a one-line change but leaving it red to show the failing-CI case.

## Findings
