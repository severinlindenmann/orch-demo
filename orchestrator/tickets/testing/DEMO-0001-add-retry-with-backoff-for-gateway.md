---
id: DEMO-0001
title: Add retry with backoff for gateway downloads
type: feature
priority: normal
size: s
status: testing
created: 2026-10-02T07:43Z
updated: 2026-10-02T07:47Z
external:
- key: '1'
  url: https://github.com/severinlindenmann/orch-demo/issues/1
repos:
- acme-energy-data
branches:
  acme-energy-data: feature/DEMO-0001-retry-gateway-downloads
worktrees: {}
prs:
- repo: acme-energy-data
  url: https://github.com/severinlindenmann/orch-demo/pull/19
  state: draft
parent: null
blocked_by: []
follow_ups: []
labels: []
gates:
  requirements:
    approved: 2026-10-02T07:47Z
    via: tty
    hash: sha256:c4d0ebf1714cae8fae029ce42d3fb5acc8ccbef87f0d1f08aed93e10e979a10e
  plan:
    approved: 2026-10-02T07:47Z
    via: tty
    hash: sha256:50a1627ab1713aab8dc8888e4b3073578c2e114f0b02f4537edaed47ac765af9
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

# DEMO-0001 — Add retry with backoff for gateway downloads

## Ask

## Context

## Requirements

- A download from a substation gateway may time out transiently.
- Retries must use backoff and give up after a bounded number of attempts.
- Every attempt (success or failure) must be logged with the gateway id.

## Acceptance criteria

- [ ] fetch_with_retry retries up to max_attempts times
- [ ] Backoff is applied between attempts
- [ ] The last exception is re-raised after attempts are exhausted
- [ ] Unit tests cover both the eventual-success and always-fails cases

## Out of scope

- Wiring fetch_with_retry into the nightly job runner itself (follow-up ticket).

## Proposal

## Plan

1. Add fetch_with_retry(download_fn, gateway_id, max_attempts) to acme.ingest.
2. Linear backoff (0.5s * attempt) between retries; log each failed attempt.
3. Re-raise the last exception once attempts are exhausted.
4. Unit tests with a fake flaky callable (fails N times then succeeds; always fails).

## Current state

## Verification

- `pytest -q` — 12 passed locally on the feature branch.
- CI run (GitHub Actions, PR #19): green — https://github.com/severinlindenmann/orch-demo/pull/19/checks
- Manually exercised fetch_with_retry with a callable that fails twice then succeeds, and one that always fails — behaves as specified.

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
- 2026-10-02T07:47Z [claude-code cc8b] linked branch feature/DEMO-0001-retry-gateway-downloads
- 2026-10-02T07:47Z [claude-code cc8b] linked pr https://github.com/severinlindenmann/orch-demo/pull/19
- 2026-10-02T07:47Z [claude-code cc8b] fetch_with_retry implemented with linear backoff; 2 new tests added, suite green locally
- 2026-10-02T07:47Z [claude-code cc8b] updated Verification
- 2026-10-02T07:47Z [claude-code cc8b] moved in-progress → testing
- 2026-10-02T07:47Z [claude-code cc8b] PR #19 open, CI green, awaiting human review

## Findings
