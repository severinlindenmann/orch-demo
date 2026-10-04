---
id: DEMO-0025
title: Tag every job with cost_center
type: chore
priority: normal
size: s
status: in-progress
created: 2026-10-02T08:11Z
updated: 2026-10-02T08:49Z
external:
- key: GH-34
  url: https://github.com/severinlindenmann/orch-demo/issues/34
repos:
- infra
branches:
  infra: chore/DEMO-0025-cost-center-tags
worktrees: {}
prs:
- repo: infra
  url: https://github.com/severinlindenmann/orch-demo-infra/pull/1
  state: draft
parent: null
blocked_by: []
follow_ups: []
labels: []
gates:
  requirements:
    approved: 2026-10-02T08:35Z
    via: tty
    hash: sha256:ed2a78588ec72064c2d95637fac57adee852decfae0759e7f66b33f32abfb47c
    hash_v: 3
  plan:
    approved: 2026-10-02T08:43Z
    via: tty
    hash: sha256:59e4f2947f9c9948524620efb01c4e7ad0845925dd8a03997698ffaea6475c3c
    hash_v: 3
  verify:
    verdict: null
    at: null
    via: null
questions: []
claim:
  session: cbbd142b-4864-5f3b-b20b-d67cbc779009
  harness: copilot
  at: 2026-10-02T08:37Z
sessions:
- id: cbbd142b-4864-5f3b-b20b-d67cbc779009
  harness: copilot
  model: null
  started: 2026-10-02T08:37Z
---

# DEMO-0025 — Tag every job with cost_center

## Requirements

- Every job file carries tags.cost_center.
- CI refuses a job without it.

## Acceptance criteria

- [ ] All jobs in acme-infra have cost_center
- [ ] CI fails without it

## Plan

1. Add cost_center to every job file.
2. Make CI require it.
3. Backfill the tag on the jobs already running on int.

## Tasks

- [/] T1 Add cost_center to every job file
  - ref: file:infra/jobs/acme_ingest_daily.json

## Log

- 2026-10-02T08:11Z [copilot cbbd] created
- 2026-10-02T08:33Z [copilot cbbd] updated Requirements
- 2026-10-02T08:33Z [copilot cbbd] updated Acceptance criteria
- 2026-10-02T08:35Z [you] approved requirements → open
- 2026-10-02T08:37Z [copilot cbbd] claimed (open → in-progress)
- 2026-10-02T08:39Z [copilot cbbd] updated Plan
- 2026-10-02T08:41Z [copilot cbbd] added T1
- 2026-10-02T08:43Z [you] approved plan
- 2026-10-02T08:45Z [copilot cbbd] started T1
- 2026-10-02T08:47Z [copilot cbbd] linked branch chore/DEMO-0025-cost-center-tags, pr https://github.com/severinlindenmann/orch-demo-infra/pull/1
- 2026-10-02T08:49Z [copilot cbbd] updated Plan
