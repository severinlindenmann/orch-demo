---
id: DEMO-0008
title: Document dbt-vs-plain-SQL spike outcome
type: spike
priority: normal
size: xs
status: done
created: 2026-10-02T07:43Z
updated: 2026-10-02T07:47Z
external:
- key: '2'
  url: https://github.com/severinlindenmann/orch-demo/issues/2
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
    hash: sha256:d972bbfbecd3712fdbf71d0e7bc5a85f57c27b70b019ea3cf245c847ba3b0b09
  plan:
    approved: null
    via: null
    hash: null
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

# DEMO-0008 — Document dbt-vs-plain-SQL spike outcome

## Ask

## Context

## Requirements

- Decide whether to adopt dbt-core for sql/staging and sql/marts, or keep the current hand-rolled SQL + thin runner.

## Acceptance criteria

- [ ] Comparison written up: what dbt buys us vs. migration cost for the 4 existing models
- [ ] Explicit recommendation with a revisit trigger
- [ ] Outcome posted where the team can find it later

## Out of scope

- Actually implementing a dbt migration (would be its own ticket if we decide to go ahead).

## Proposal

## Plan

## Current state

## Verification

- Comparison posted: https://github.com/severinlindenmann/orch-demo/issues/2
- Decision: not now; revisit once we have more than ~10 SQL models.

## Decisions

## Log

- 2026-10-02T07:43Z [claude-code cc8b] created
- 2026-10-02T07:47Z [claude-code cc8b] updated Requirements
- 2026-10-02T07:47Z [claude-code cc8b] updated Acceptance criteria
- 2026-10-02T07:47Z [claude-code cc8b] updated Out of scope
- 2026-10-02T07:47Z [you] approved requirements → open
- 2026-10-02T07:47Z [claude-code cc8b] claimed (open → in-progress)
- 2026-10-02T07:47Z [claude-code cc8b] Drafted the comparison and posted it as a comment on issue #2. Opened PR #24 with a standalone sql/README.md, then decided to close it unmerged and keep the write-up as an issue comment instead so we don't carry a doc file that goes stale.
- 2026-10-02T07:47Z [claude-code cc8b] updated Verification
- 2026-10-02T07:47Z [claude-code cc8b] moved in-progress → testing
- 2026-10-02T07:47Z [you] verdict done: Decision recorded on issue #2; no further action needed now.

## Findings
