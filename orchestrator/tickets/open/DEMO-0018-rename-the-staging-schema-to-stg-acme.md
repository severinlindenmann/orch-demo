---
id: DEMO-0018
title: Rename the staging schema to stg_acme
type: chore
priority: low
size: s
status: open
created: 2026-10-02T07:57Z
updated: 2026-10-02T16:35Z
external:
- key: GH-27
  url: https://github.com/severinlindenmann/orch-demo/issues/27
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
    approved: 2026-10-02T16:33Z
    via: tty
    hash: sha256:f02d86ed8e4b2b4768c54fabab5bd1f004946efbbc9aa03658a7a8ccedf52000
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

# DEMO-0018 — Rename the staging schema to stg_acme

## Requirements

- Rename the staging schema from staging to stg_acme.
- Keep a view in the old schema for one sprint so dashboards keep working.

## Acceptance criteria

- [ ] All staging models build into stg_acme
- [ ] No mart references the old schema

## Log

- 2026-10-02T07:57Z [claude-code fdba] created
- 2026-10-02T16:31Z [claude-code fdba] updated Requirements
- 2026-10-02T16:31Z [claude-code fdba] updated Acceptance criteria
- 2026-10-02T16:33Z [you] approved requirements → open
- 2026-10-02T16:35Z [claude-code fdba] updated Requirements
