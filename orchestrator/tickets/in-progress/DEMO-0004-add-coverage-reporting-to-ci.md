---
id: DEMO-0004
title: Add coverage reporting to CI
type: chore
priority: normal
size: s
status: in-progress
created: 2026-10-02T07:43Z
updated: 2026-10-04T14:21Z
external:
- key: GH-4
  url: https://github.com/severinlindenmann/orch-demo/issues/4
repos:
- acme-energy-data
branches:
  acme-energy-data: feature/DEMO-0004-coverage-reporting
worktrees: {}
prs:
- repo: acme-energy-data
  url: https://github.com/severinlindenmann/orch-demo/pull/22
  state: draft
parent: null
blocked_by: []
follow_ups: []
labels: []
gates:
  requirements:
    approved: 2026-10-02T07:47Z
    via: tty
    hash: sha256:eb23c1bdeb9e2b0b6152eff679ef647a202f983a93df97bd8ff1903a60f8e69a
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
  session: cc8be880-3610-520a-8cce-3b15f6753080
  harness: claude-code
  at: 2026-10-04T14:21Z
sessions:
- id: cc8be880-3610-520a-8cce-3b15f6753080
  harness: claude-code
  model: null
  started: 2026-10-02T07:47Z
---

# DEMO-0004 — Add coverage reporting to CI

## Requirements

- CI must report per-module coverage so we can see what's under-tested.
- No behavior change to what passes/fails CI yet, visibility only.

## Acceptance criteria

- [ ] CI runs pytest with --cov=acme --cov-report=term-missing
- [ ] Coverage summary appears in the GitHub Actions log
- [ ] No hard coverage gate introduced in this change

## Out of scope

- Deciding on and enforcing a minimum coverage percentage (needs a follow-up decision).

## Plan

1. Add pytest-cov to the dev extras.
2. Update ci.yml to run pytest with --cov=acme --cov-report=term-missing.
3. Open question for the human: do we want a hard coverage gate now, and at what percentage? Holding this PR as draft until that's decided.

## Log

- 2026-10-02T07:43Z [claude-code cc8b] created
- 2026-10-02T07:47Z [claude-code cc8b] updated Requirements
- 2026-10-02T07:47Z [claude-code cc8b] updated Acceptance criteria
- 2026-10-02T07:47Z [claude-code cc8b] updated Out of scope
- 2026-10-02T07:47Z [claude-code cc8b] updated Plan
- 2026-10-02T07:47Z [you] approved requirements → open
- 2026-10-02T07:47Z [claude-code cc8b] claimed (open → in-progress)
- 2026-10-02T07:47Z [claude-code cc8b] linked branch feature/DEMO-0004-coverage-reporting
- 2026-10-02T07:47Z [claude-code cc8b] linked pr https://github.com/severinlindenmann/orch-demo/pull/22
- 2026-10-02T07:47Z [claude-code cc8b] Plan drafted and PR #22 opened as draft. Holding here for the human to approve the Plan gate and decide whether to add a hard coverage threshold before marking ready.
- 2026-10-04T14:20Z [you] adopted the unsigned gate requirements into the ledger
- 2026-10-02T07:48Z [you] edited the ticket file
- 2026-10-04T14:21Z [claude-code cc8b] claimed
