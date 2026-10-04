---
id: DEMO-0036
title: Alert when a gateway fails three runs in a row
type: feature
priority: normal
size: s
status: open
created: 2026-10-03T08:28Z
updated: 2026-10-04T11:15Z
external: []
repos: []
branches: {}
worktrees: {}
prs: []
parent: DEMO-0031
sprint: S2
blocked_by: []
follow_ups: []
labels: []
gates:
  requirements:
    approved: 2026-10-03T08:32Z
    via: cli
    hash: sha256:6f01162ce36193f5c80473381beff02aedff29e94c1c3f1eacd8a7f0a598a22b
    hash_v: 3
    epic: DEMO-0031
    delegation: sha256:99667fdd79d4675f5845ad4ddf9c1003b3944e69088e59483a111827c26d4b9d
  plan:
    approved: 2026-10-03T08:32Z
    via: cli
    hash: sha256:7e2ea0f02e89c9cdd385910285dae5b502850ec7e8036dcbe5cacd6c7b02c4d3
    hash_v: 3
    epic: DEMO-0031
    delegation: sha256:99667fdd79d4675f5845ad4ddf9c1003b3944e69088e59483a111827c26d4b9d
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

# DEMO-0036 — Alert when a gateway fails three runs in a row

## Requirements

- Raise an alert when the same gateway fails three consecutive runs.

## Acceptance criteria

- [ ] Three failures in a row raise one alert
- [ ] A success in between resets the count

## Plan

Count consecutive failures per gateway in the run log and alert at three.

## Log

- 2026-10-03T08:28Z [claude-code 20d1] created in epic DEMO-0031
- 2026-10-03T08:30Z [claude-code 20d1] updated Requirements
- 2026-10-03T08:30Z [claude-code 20d1] updated Acceptance criteria
- 2026-10-03T08:30Z [claude-code 20d1] updated Plan
- 2026-10-03T08:32Z [claude-code 20d1] auto-approved requirements and plan under the delegation of epic DEMO-0031
- 2026-10-04T11:15Z [claude-code 20d1] linked sprint S2
