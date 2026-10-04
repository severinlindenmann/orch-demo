---
id: DEMO-0006
title: Skip malformed CSV rows instead of aborting the file
type: bug
priority: high
size: s
status: done
created: 2026-10-02T07:43Z
updated: 2026-10-02T07:48Z
external:
- key: GH-7
  url: https://github.com/severinlindenmann/orch-demo/issues/7
repos:
- acme-energy-data
branches:
  acme-energy-data: fix/DEMO-0006-ingest-malformed-rows
worktrees: {}
prs:
- repo: acme-energy-data
  url: https://github.com/severinlindenmann/orch-demo/pull/16
  state: draft
parent: null
blocked_by: []
follow_ups: []
labels: []
gates:
  requirements:
    approved: 2026-10-02T07:47Z
    via: tty
    hash: sha256:2b7217095ec95a9caa12ed8d159e4bfe3c5b1277826c7089a592d35b45c08c5c
  plan:
    approved: 2026-10-02T07:47Z
    via: tty
    hash: sha256:d3f706fc9d911075777d7986549600f0612daf9101ed437297ce1a41bb6f497d
  verify:
    verdict: done
    at: 2026-10-02T07:47Z
    via: tty
questions: []
claim:
  session: null
  harness: null
  at: null
sessions:
- id: cc8be880-3610-520a-8cce-3b15f6753080
  harness: claude-code
  model: null
  started: 2026-10-02T07:47Z
---

# DEMO-0006 — Skip malformed CSV rows instead of aborting the file

## Requirements

- A single malformed row in a gateway export must not abort the whole file.
- Malformed rows must be logged with enough detail to trace back to the source file.

## Acceptance criteria

- [ ] parse_gateway_export skips a malformed row and logs file name + line number
- [ ] The rest of a file with one bad row among good ones is still ingested
- [ ] Regression test for a file with a mixed good/bad row set

## Out of scope

- Alerting on a sustained rate of malformed rows (separate ticket if it recurs).

## Plan

1. Wrap the per-row parse in try/except in parse_gateway_export.
2. Log a warning with file name, line number and the row contents on failure.
3. Regression test: 3-row file with 1 malformed row in the middle.

## Verification

- `pytest -q` — 9 passed locally.
- CI run (PR #16): green — https://github.com/severinlindenmann/orch-demo/pull/16/checks
- Merged to main via squash merge.

## Log

- 2026-10-02T07:43Z [claude-code cc8b] created
- 2026-10-02T07:47Z [claude-code cc8b] updated Requirements
- 2026-10-02T07:47Z [claude-code cc8b] updated Acceptance criteria
- 2026-10-02T07:47Z [claude-code cc8b] updated Out of scope
- 2026-10-02T07:47Z [claude-code cc8b] updated Plan
- 2026-10-02T07:47Z [you] approved requirements → open
- 2026-10-02T07:47Z [claude-code cc8b] claimed (open → in-progress)
- 2026-10-02T07:47Z [you] approved plan
- 2026-10-02T07:47Z [claude-code cc8b] linked branch fix/DEMO-0006-ingest-malformed-rows
- 2026-10-02T07:47Z [claude-code cc8b] linked pr https://github.com/severinlindenmann/orch-demo/pull/16
- 2026-10-02T07:47Z [claude-code cc8b] updated Verification
- 2026-10-02T07:47Z [claude-code cc8b] moved in-progress → testing
- 2026-10-02T07:47Z [you] verdict done: Merged PR #16 (squash). Issue #7 closed.
- 2026-10-04T14:21Z [you] adopted the unsigned gate requirements into the ledger
- 2026-10-04T14:21Z [you] adopted the unsigned gate plan into the ledger
- 2026-10-04T14:21Z [you] adopted the unsigned verdict into the ledger
- 2026-10-02T07:48Z [you] edited the ticket file
