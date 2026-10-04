---
id: DEMO-0022
title: Use meter_type in the suspect-threshold mart
type: feature
priority: normal
size: m
status: open
created: 2026-10-02T08:05Z
updated: 2026-10-02T19:15Z
external:
- key: GH-31
  url: https://github.com/severinlindenmann/orch-demo/issues/31
repos: []
branches: {}
worktrees: {}
prs: []
parent: null
blocked_by:
- DEMO-0021
follow_ups: []
labels: []
gates:
  requirements:
    approved: 2026-10-02T19:13Z
    via: tty
    hash: sha256:83cba4708529ec5256a069ce55953d32c0191fa5d24f174e4ba64ff3d7c89a17
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

# DEMO-0022 — Use meter_type in the suspect-threshold mart

## Requirements

- Pick the suspect threshold per meter type from dim_meter_type.

## Acceptance criteria

- [ ] Each meter type has its own threshold
- [ ] The mart builds in under 5 min

## Log

- 2026-10-02T08:05Z [claude-code b5f7] created
- 2026-10-02T19:11Z [claude-code b5f7] updated Requirements
- 2026-10-02T19:11Z [claude-code b5f7] updated Acceptance criteria
- 2026-10-02T19:13Z [you] approved requirements → open
- 2026-10-02T19:15Z [you] edited the ticket file
