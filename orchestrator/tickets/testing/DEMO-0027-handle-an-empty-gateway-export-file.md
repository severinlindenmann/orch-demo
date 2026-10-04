---
id: DEMO-0027
title: Handle an empty gateway export file
type: bug
priority: high
size: xs
status: testing
created: 2026-10-02T08:15Z
updated: 2026-10-03T06:10Z
external:
- key: GH-36
  url: https://github.com/severinlindenmann/orch-demo/issues/36
repos:
- ingest
branches:
  ingest: fix/DEMO-0027-empty-export
worktrees: {}
prs:
- repo: ingest
  url: https://github.com/severinlindenmann/orch-demo-ingest/pull/4
  state: draft
parent: null
blocked_by: []
follow_ups: []
labels: []
gates:
  requirements:
    approved: 2026-10-03T05:50Z
    via: tty
    hash: sha256:5efb8917ccca641bc483d47a858ca3052bad4279c02a8e1a63d3de2a3b811527
    hash_v: 3
  plan:
    approved: null
    via: null
    hash: null
  verify:
    verdict: null
    at: null
    via: null
questions:
- id: Q1
  text: 'An empty export: skip it silently or log a warning?'
  why: Ops want to notice dead gateways.
  type: single
  options:
  - key: A
    label: Skip silently
    cost: nobody notices a dead gateway
  - key: B
    label: Skip and log a warning
    cost: one log line per empty file
  recommended: B
  blocking: true
  asked: 2026-10-03T05:54Z
  answer: B
  note: warn, so ops see dead gateways
  answered: 2026-10-03T05:56Z
  via: tty
claim:
  session: a8e3ecb4-2fb5-53ef-a26e-d1e723e3063a
  harness: claude-code
  at: 2026-10-03T05:52Z
sessions:
- id: a8e3ecb4-2fb5-53ef-a26e-d1e723e3063a
  harness: claude-code
  model: null
  started: 2026-10-03T05:52Z
artifacts:
- name: empty-export-tests.log
  kind: log
  sha256: ddeb535633927fe2f710a5dd7b35f1b643c0e99f1c4cb36d9a850360c7d3736a
  size: 153
  added: 2026-10-03T06:08Z
  label: Test run with the empty-export tests
  task: T1
  ac: 1
---

# DEMO-0027 — Handle an empty gateway export file

## Requirements

- An empty export returns no rows instead of crashing.

## Acceptance criteria

- [ ] A test covers the empty file

## Tasks

- [x] T1 Return no rows for an empty export
  - ref: file:ingest/src/acme_ingest/download.py
  - verify: python -m unittest discover -s tests -t .
  - note: test_empty_export passes on fix/DEMO-0027-empty-export

## Verification

`python -m unittest discover -s tests -t .` in ingest: 14 tests OK, including test_empty_export.

## Log

- 2026-10-02T08:15Z [claude-code a8e3] created
- 2026-10-03T05:48Z [claude-code a8e3] updated Requirements
- 2026-10-03T05:48Z [claude-code a8e3] updated Acceptance criteria
- 2026-10-03T05:50Z [you] approved requirements → open
- 2026-10-03T05:52Z [claude-code a8e3] claimed (open → in-progress)
- 2026-10-03T05:54Z [claude-code a8e3] asked Q1 → waiting
- 2026-10-03T05:56Z [you] answered Q1: B — warn, so ops see dead gateways → in-progress
- 2026-10-03T05:58Z [claude-code a8e3] added T1
- 2026-10-03T06:00Z [claude-code a8e3] started T1
- 2026-10-03T06:02Z [claude-code a8e3] T1 done: test_empty_export passes on fix/DEMO-0027-empty-export
- 2026-10-03T06:04Z [claude-code a8e3] linked branch fix/DEMO-0027-empty-export, pr https://github.com/severinlindenmann/orch-demo-ingest/pull/4
- 2026-10-03T06:06Z [claude-code a8e3] updated Verification
- 2026-10-03T06:08Z [claude-code a8e3] added artifact empty-export-tests.log (log) for T1 for AC1
- 2026-10-03T06:10Z [claude-code a8e3] moved in-progress → testing
