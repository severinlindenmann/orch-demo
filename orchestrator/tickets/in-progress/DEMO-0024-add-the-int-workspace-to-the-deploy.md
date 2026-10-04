---
id: DEMO-0024
title: Add the int workspace to the deploy targets
type: feature
priority: normal
size: m
status: in-progress
created: 2026-10-02T08:09Z
updated: 2026-10-04T14:21Z
external:
- key: GH-33
  url: https://github.com/severinlindenmann/orch-demo/issues/33
repos: []
branches: {}
worktrees: {}
prs: []
parent: null
sprint: S1
blocked_by: []
follow_ups: []
labels: []
gates:
  requirements:
    approved: 2026-10-03T21:47Z
    via: tty
    hash: sha256:34faa8c73a983949fd49b1cdf3a526f96985c15f96919ab72eced4a204c4f97b
    hash_v: 3
  plan:
    approved: null
    via: null
    hash: null
    changes_requested:
      at: 2026-10-03T21:53Z
      by: you
      message: Keep int and prod in separate files with no shared defaults, then ask me again.
      hash: sha256:e0e05fb6bf3bcfd7dc77633c50e5c79b4e6b2fa3be7a00389abf1119189599c1
  verify:
    verdict: null
    at: null
    via: null
questions: []
claim:
  session: 2d87c094-d3c9-5c1f-916e-5e04b5b60141
  harness: claude-code
  at: 2026-10-04T14:21Z
sessions:
- id: 2d87c094-d3c9-5c1f-916e-5e04b5b60141
  harness: claude-code
  model: null
  started: 2026-10-03T21:49Z
---

# DEMO-0024 — Add the int workspace to the deploy targets

## Requirements

- Add an int target next to dev and prod.

## Acceptance criteria

- [ ] envs/int.json is validated by CI
- [ ] Runbook updated

## Plan

Add int to envs/ and share defaults with prod through a common file.

## Log

- 2026-10-02T08:09Z [claude-code 2d87] created
- 2026-10-03T21:45Z [claude-code 2d87] updated Requirements
- 2026-10-03T21:45Z [claude-code 2d87] updated Acceptance criteria
- 2026-10-03T21:47Z [you] approved requirements → open
- 2026-10-03T21:49Z [claude-code 2d87] claimed (open → in-progress)
- 2026-10-03T21:51Z [claude-code 2d87] updated Plan
- 2026-10-03T21:53Z [you] asked for changes on the plan: Keep int and prod in separate files with no shared defaults, then ask me again.
- 2026-10-04T11:07Z [claude-code 2d87] linked sprint S1
- 2026-10-04T14:21Z [claude-code 2d87] claimed
