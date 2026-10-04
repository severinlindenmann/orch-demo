---
id: DEMO-0005
title: Pin dependency upper bounds
type: chore
priority: normal
size: xs
status: waiting
created: 2026-10-02T07:43Z
updated: 2026-10-02T07:48Z
external:
- key: GH-15
  url: https://github.com/severinlindenmann/orch-demo/issues/15
repos:
- acme-energy-data
branches:
  acme-energy-data: chore/DEMO-0005-pin-dependency-versions
worktrees: {}
prs:
- repo: acme-energy-data
  url: https://github.com/severinlindenmann/orch-demo/pull/18
  state: draft
parent: null
blocked_by: []
follow_ups: []
labels: []
gates:
  requirements:
    approved: 2026-10-02T07:47Z
    via: tty
    hash: sha256:392ac8167172e47443aeceb10071b0dc5a981be2f865cdd830ac2038fa298502
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
  text: 'main already pins these dependencies — how should PR #18 be reconciled?'
  why: main and this branch both touched the same two dependency lines.
  type: single
  options:
  - key: A
    label: Rebase this branch onto main and keep main's bounds
    cost: small
  - key: B
    label: Close this PR; main's pin already covers the need
    cost: lose the README doc change unless reapplied
  - key: C
    label: Merge main into the branch and reconcile both sets of bounds by hand
    cost: slightly more review effort
  recommended: A
  blocking: true
  asked: 2026-10-02T07:47Z
  answer: null
  note: null
  answered: null
  via: null
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

# DEMO-0005 — Pin dependency upper bounds

## Requirements

- Direct dependencies (pandas, pydantic) need explicit upper bounds.
- The refresh process for bumping a pin must be documented.

## Acceptance criteria

- [ ] pandas and pydantic carry upper bounds in pyproject.toml
- [ ] README documents how to refresh a pin
- [ ] CI stays green with the new bounds

## Out of scope

- Introducing a full lockfile (uv.lock / poetry.lock) — separate decision.

## Log

- 2026-10-02T07:43Z [claude-code cc8b] created
- 2026-10-02T07:47Z [claude-code cc8b] updated Requirements
- 2026-10-02T07:47Z [claude-code cc8b] updated Acceptance criteria
- 2026-10-02T07:47Z [claude-code cc8b] updated Out of scope
- 2026-10-02T07:47Z [you] approved requirements → open
- 2026-10-02T07:47Z [copilot cc8b] claimed (open → in-progress)
- 2026-10-02T07:47Z [claude-code cc8b] linked branch chore/DEMO-0005-pin-dependency-versions
- 2026-10-02T07:47Z [claude-code cc8b] linked pr https://github.com/severinlindenmann/orch-demo/pull/18
- 2026-10-02T07:47Z [copilot cc8b] PR #18 opened. main has since picked a different, incompatible pin (DEMO-0005 commit landed directly on main instead of through this PR), so #18 now shows a merge conflict on pyproject.toml.
- 2026-10-02T07:47Z [claude-code cc8b] asked Q1 → waiting
- 2026-10-04T14:21Z [you] adopted the unsigned gate requirements into the ledger
- 2026-10-02T07:48Z [you] edited the ticket file
