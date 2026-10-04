---
id: DEMO-0033
title: Validate gateway export checksums
type: feature
priority: normal
size: m
status: open
created: 2026-10-02T08:27Z
updated: 2026-10-04T11:13Z
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
    approved: 2026-10-02T19:19Z
    via: tty
    hash: sha256:f2dc6e1e7e9113b43b10ab43566ce686c900ca22f456a2c812db0253dbb2062c
    hash_v: 3
    epic: DEMO-0031
  plan:
    approved: 2026-10-02T19:19Z
    via: tty
    hash: sha256:ecf143a08d7894d6918a9653449d30da1008e41cd6d0861e04f6b1690b8e711c
    hash_v: 3
    epic: DEMO-0031
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

# DEMO-0033 — Validate gateway export checksums

## Requirements

- Reject an export whose SHA-256 does not match the gateway's manifest.
- Also reject an export that has no manifest entry at all.

## Acceptance criteria

- [ ] A corrupt export is rejected with its file name
- [ ] Valid exports load as before

## Plan

Read the manifest next to each export and compare hashes before staging.

## Log

- 2026-10-02T08:27Z [copilot 8e56] created in epic DEMO-0031
- 2026-10-02T18:23Z [copilot 8e56] updated Requirements
- 2026-10-02T18:23Z [copilot 8e56] updated Acceptance criteria
- 2026-10-02T18:23Z [copilot 8e56] updated Plan
- 2026-10-02T19:19Z [you] approved with epic DEMO-0031: requirements and plan
- 2026-10-03T06:12Z [copilot 8e56] updated Requirements
- 2026-10-04T11:13Z [copilot 8e56] linked sprint S2
