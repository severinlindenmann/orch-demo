---
id: DEMO-0019
title: Move the gateway download into the ingest service
type: feature
priority: normal
size: l
status: in-progress
created: 2026-10-02T07:59Z
updated: 2026-10-04T14:21Z
external:
- key: GH-28
  url: https://github.com/severinlindenmann/orch-demo/issues/28
repos:
- ingest
- infra
- acme-energy-data
branches:
  ingest: feature/DEMO-0019-gateway-client
  infra: feature/DEMO-0019-ingest-service-job
  acme-energy-data: feature/DEMO-0019-remove-old-download
worktrees: {}
prs:
- repo: ingest
  url: https://github.com/severinlindenmann/orch-demo-ingest/pull/2
  state: draft
- repo: infra
  url: https://github.com/severinlindenmann/orch-demo-infra/pull/3
  state: draft
parent: null
sprint: S1
blocked_by: []
follow_ups: []
labels: []
gates:
  requirements:
    approved: 2026-10-04T05:45Z
    via: tty
    hash: sha256:f157e67c0e486218caeab31ea445cc91733c366edf963ed249bc24bf22391661
    hash_v: 3
  plan:
    approved: 2026-10-04T05:53Z
    via: tty
    hash: sha256:f35b5f82273fa99f162a9ad491e5f4a32eb902dd8b0d73f139410e4bf95fee1f
    hash_v: 3
  verify:
    verdict: null
    at: null
    via: null
questions: []
claim:
  session: c8a99367-1495-5540-ac8e-0752698392b1
  harness: copilot
  at: 2026-10-04T14:21Z
sessions:
- id: c8a99367-1495-5540-ac8e-0752698392b1
  harness: copilot
  model: null
  started: 2026-10-04T05:47Z
---

# DEMO-0019 — Move the gateway download into the ingest service

## Requirements

- Move the gateway download code from acme-energy-data into acme-ingest.
- Run it as its own job defined in acme-infra.
- acme-energy-data only reads the downloaded files.

## Acceptance criteria

- [ ] acme-ingest downloads every gateway with backoff
- [ ] jobs/acme_ingest_service.json exists in acme-infra
- [ ] src/acme/ingest.py no longer downloads anything

## Out of scope

- Changing the export format.

## Plan

1. Copy the client into acme-ingest with tests.
2. Add the job definition in acme-infra.
3. Remove the old download code here.
4. Merge order: ingest, then infra, then acme-energy-data.

## Tasks

- [x] T1 Copy the download client into acme-ingest
  - ref: file:ingest/src/acme_ingest/download.py
  - verify: python -m unittest discover -s tests -t .
  - note: unit tests green on feature/DEMO-0019-gateway-client
- [/] T2 Add the ingest service job to acme-infra
  - ref: file:infra/jobs/acme_ingest_daily.json
  - needs: T1
- [ ] T3 Remove the old download code from acme-energy-data
  - ref: file:src/acme/ingest.py
  - needs: T1, T2
- [ ] T4 Approve the service principal for the new job
  - owner: human

## Current state

T1 is done; its ingest PR waits for your review. T2 is a draft PR in acme-infra. T3 starts after both merge.

## Log

- 2026-10-02T07:59Z [copilot c8a9] created
- 2026-10-04T05:43Z [copilot c8a9] updated Requirements
- 2026-10-04T05:43Z [copilot c8a9] updated Acceptance criteria
- 2026-10-04T05:43Z [copilot c8a9] updated Out of scope
- 2026-10-04T05:45Z [you] approved requirements → open
- 2026-10-04T05:47Z [copilot c8a9] claimed (open → in-progress)
- 2026-10-04T05:49Z [copilot c8a9] updated Plan
- 2026-10-04T05:51Z [copilot c8a9] added T1, T2, T3, T4
- 2026-10-04T05:53Z [you] approved plan
- 2026-10-04T05:55Z [copilot c8a9] started T1
- 2026-10-04T05:57Z [copilot c8a9] T1 done: unit tests green on feature/DEMO-0019-gateway-client
- 2026-10-04T05:59Z [copilot c8a9] started T2
- 2026-10-04T06:01Z [copilot c8a9] linked branch feature/DEMO-0019-gateway-client, pr https://github.com/severinlindenmann/orch-demo-ingest/pull/2
- 2026-10-04T06:03Z [copilot c8a9] linked branch feature/DEMO-0019-ingest-service-job, pr https://github.com/severinlindenmann/orch-demo-infra/pull/3
- 2026-10-04T06:05Z [copilot c8a9] linked branch feature/DEMO-0019-remove-old-download
- 2026-10-04T06:07Z [copilot c8a9] updated current state
- 2026-10-04T11:04Z [copilot c8a9] linked sprint S1
- 2026-10-04T14:21Z [copilot c8a9] claimed
