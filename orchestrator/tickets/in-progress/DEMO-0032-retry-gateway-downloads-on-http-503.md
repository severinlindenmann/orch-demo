---
id: DEMO-0032
title: Retry gateway downloads on HTTP 503
type: feature
priority: high
size: s
status: in-progress
created: 2026-10-02T08:25Z
updated: 2026-10-04T14:21Z
external: []
repos: []
branches: {}
worktrees: {}
prs: []
parent: DEMO-0031
sprint: S1
blocked_by: []
follow_ups: []
labels: []
gates:
  requirements:
    approved: 2026-10-02T19:19Z
    via: tty
    hash: sha256:c868cfafd630a532fab01cae0a1369b87bfc0703563c53b15393ef459dfdb036
    hash_v: 3
    epic: DEMO-0031
  plan:
    approved: 2026-10-02T19:19Z
    via: tty
    hash: sha256:feda41784d9541635d1ed89d910cd3ea0f2c66b8dd2a959667e60f6a5d621bf3
    hash_v: 3
    epic: DEMO-0031
  verify:
    verdict: null
    at: null
    via: null
questions: []
claim:
  session: 2743f332-25d9-594f-b329-9e7981d9b538
  harness: claude-code
  at: 2026-10-04T14:21Z
sessions:
- id: 2743f332-25d9-594f-b329-9e7981d9b538
  harness: claude-code
  model: null
  started: 2026-10-02T21:18Z
---

# DEMO-0032 — Retry gateway downloads on HTTP 503

## Requirements

- Retry a download that answers HTTP 503 up to three times with backoff.

## Acceptance criteria

- [ ] A 503 then 200 sequence loads the file
- [ ] Three 503s in a row fail the run with the URL

## Plan

Wrap the download call in a retry with 2, 4 and 8 s backoff; test with a fake server.

## Tasks

- [/] T1 Retry 503 responses with backoff
  - ref: file:ingest/src/acme_ingest/download.py
  - verify: python -m unittest discover -s tests -t .
  - added: 2026-10-02T21:20Z after plan approval
- [ ] T2 Test the 503-then-200 and three-503 cases
  - verify: python -m unittest discover -s tests -t .
  - added: 2026-10-02T21:20Z after plan approval

## Log

- 2026-10-02T08:25Z [claude-code 2743] created in epic DEMO-0031
- 2026-10-02T18:07Z [claude-code 2743] updated Requirements
- 2026-10-02T18:07Z [claude-code 2743] updated Acceptance criteria
- 2026-10-02T18:07Z [claude-code 2743] updated Plan
- 2026-10-02T19:19Z [you] approved with epic DEMO-0031: requirements and plan
- 2026-10-02T21:18Z [claude-code 2743] claimed (open → in-progress)
- 2026-10-02T21:20Z [claude-code 2743] added T1, T2 after plan approval
- 2026-10-02T21:22Z [claude-code 2743] started T1
- 2026-10-04T11:09Z [claude-code 2743] linked sprint S1
- 2026-10-04T14:21Z [claude-code 2743] claimed
