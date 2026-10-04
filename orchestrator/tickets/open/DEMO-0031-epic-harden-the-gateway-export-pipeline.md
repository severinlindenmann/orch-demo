---
id: DEMO-0031
title: 'Epic: harden the gateway export pipeline'
type: epic
priority: high
size: l
status: open
created: 2026-10-02T08:23Z
updated: 2026-10-02T19:19Z
external: []
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
    approved: 2026-10-02T19:19Z
    via: tty
    hash: sha256:e81817688aa36200b1772c1f285c8b41db1f051e1f73f1c8712eeb85208599c9
    hash_v: 3
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

# DEMO-0031 — Epic: harden the gateway export pipeline

## Requirements

- Gateway exports that fail transiently are retried, not lost.
- Corrupt exports are rejected before they reach staging.
- Ops hear about a gateway that keeps failing.

## Acceptance criteria

- [ ] Every child is done or explicitly dropped
- [ ] No export lost in a week of int runs

## Log

- 2026-10-02T08:23Z [claude-code 30b0] created
- 2026-10-02T19:17Z [claude-code 30b0] updated Requirements
- 2026-10-02T19:17Z [claude-code 30b0] updated Acceptance criteria
- 2026-10-02T19:19Z [you] approved the epic with DEMO-0032, DEMO-0033 → open
