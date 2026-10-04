---
id: DEMO-0007
title: Accept DD/MM/YYYY gateway timestamps
type: bug
priority: high
size: s
status: done
created: 2026-10-02T07:43Z
updated: 2026-10-02T07:48Z
external:
- key: GH-13
  url: https://github.com/severinlindenmann/orch-demo/issues/13
repos:
- acme-energy-data
branches:
  acme-energy-data: fix/DEMO-0007-gateway-timestamp-formats
worktrees: {}
prs:
- repo: acme-energy-data
  url: https://github.com/severinlindenmann/orch-demo/pull/17
  state: draft
parent: null
blocked_by: []
follow_ups: []
labels: []
gates:
  requirements:
    approved: 2026-10-02T07:47Z
    via: tty
    hash: sha256:fa37fa945b0dd0f939bb657cd2d2cfaa094a10a8de807f31af496ecb08a594fa
  plan:
    approved: 2026-10-02T07:47Z
    via: tty
    hash: sha256:c513fcce1bd43d486c62907a6986b2f431b5af39f8f6a1d56fa0cea5d9d4ac18
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
  harness: copilot
  model: null
  started: 2026-10-02T07:47Z
---

# DEMO-0007 — Accept DD/MM/YYYY gateway timestamps

## Requirements

- Gateway exports in DD/MM/YYYY HH:MM must be accepted alongside ISO 8601.
- The alternate format must be normalized before pydantic validation.

## Acceptance criteria

- [ ] _parse_timestamp accepts both ISO 8601 and DD/MM/YYYY HH:MM
- [ ] A file using the alternate format parses successfully end to end
- [ ] Every other gateway's ISO 8601 timestamps are unaffected

## Out of scope

- Auto-detecting and supporting further timestamp formats beyond these two.

## Plan

1. Add _parse_timestamp() that tries ISO 8601 first, then the DD/MM/YYYY HH:MM format.
2. Use it for read_at before constructing RawMeterRead.
3. Regression test for a file using the alternate format.

## Verification

- `pytest -q` — 10 passed locally.
- CI run (PR #17): green — https://github.com/severinlindenmann/orch-demo/pull/17/checks
- Merged to main via squash merge.

## Log

- 2026-10-02T07:43Z [claude-code cc8b] created
- 2026-10-02T07:47Z [claude-code cc8b] updated Requirements
- 2026-10-02T07:47Z [claude-code cc8b] updated Acceptance criteria
- 2026-10-02T07:47Z [claude-code cc8b] updated Out of scope
- 2026-10-02T07:47Z [claude-code cc8b] updated Plan
- 2026-10-02T07:47Z [you] approved requirements → open
- 2026-10-02T07:47Z [copilot cc8b] claimed (open → in-progress)
- 2026-10-02T07:47Z [you] approved plan
- 2026-10-02T07:47Z [claude-code cc8b] linked branch fix/DEMO-0007-gateway-timestamp-formats
- 2026-10-02T07:47Z [claude-code cc8b] linked pr https://github.com/severinlindenmann/orch-demo/pull/17
- 2026-10-02T07:47Z [claude-code cc8b] updated Verification
- 2026-10-02T07:47Z [copilot cc8b] moved in-progress → testing
- 2026-10-02T07:47Z [you] verdict done: Merged PR #17 (squash). Issue #13 closed.
- 2026-10-04T14:21Z [you] adopted the unsigned gate requirements into the ledger
- 2026-10-04T14:21Z [you] adopted the unsigned gate plan into the ledger
- 2026-10-04T14:21Z [you] adopted the unsigned verdict into the ledger
- 2026-10-02T07:48Z [you] edited the ticket file
