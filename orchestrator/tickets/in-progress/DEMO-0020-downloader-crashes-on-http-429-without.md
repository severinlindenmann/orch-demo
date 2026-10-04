---
id: DEMO-0020
title: Downloader crashes on HTTP 429 without Retry-After
type: bug
priority: urgent
size: s
status: in-progress
created: 2026-10-02T08:01Z
updated: 2026-10-04T14:21Z
external:
- key: GH-29
  url: https://github.com/severinlindenmann/orch-demo/issues/29
repos:
- ingest
branches:
  ingest: fix/DEMO-0020-handle-429
worktrees: {}
prs:
- repo: ingest
  url: https://github.com/severinlindenmann/orch-demo-ingest/pull/1
  state: draft
parent: null
sprint: S1
blocked_by: []
follow_ups: []
labels: []
gates:
  requirements:
    approved: 2026-10-04T08:24Z
    via: tty
    hash: sha256:0a4ab953980772274de804e6d7f3497fbc425fac4c8e3ab170c224cb87b1d7fa
    hash_v: 3
  plan:
    approved: 2026-10-04T08:32Z
    via: tty
    hash: sha256:e1be93e760d3e03192b1c545a289523c4a9d64ac9fac03504bdd2b8bd56ea186
    hash_v: 3
  verify:
    verdict: null
    at: null
    via: null
questions: []
claim:
  session: 45e35752-5545-5d55-891b-2418be634a59
  harness: claude-code
  at: 2026-10-04T14:21Z
sessions:
- id: 45e35752-5545-5d55-891b-2418be634a59
  harness: claude-code
  model: null
  started: 2026-10-04T08:26Z
artifacts:
- name: 429-repro.log
  kind: log
  sha256: 654c10063ea81dc7f31c753f966adea807f1db3e67bc03dd64ce907e098802f5
  size: 244
  added: 2026-10-04T08:42Z
  label: Unit tests after the 429 fix
  task: T1
  ac: 1
- url: https://github.com/severinlindenmann/orch-demo-ingest/pull/1/checks
  kind: build
  added: 2026-10-04T08:44Z
  label: CI run on the fix PR
  task: T2
  ac: 2
---

# DEMO-0020 — Downloader crashes on HTTP 429 without Retry-After

## Context

acme-ingest crashes when a gateway answers 429 without Retry-After (seen on gw-07).

## Requirements

- Back off 30 s on HTTP 429 when Retry-After is missing.

## Acceptance criteria

- [ ] A test reproduces the crash
- [ ] The downloader waits 30 s and retries

## Plan

Reproduce with a test first, then back off 30 s when Retry-After is missing.

## Tasks

- [x] T1 Reproduce the crash with a 429 test
  - ref: file:ingest/tests/test_download.py
  - note: test_429_without_retry_after_waits_30s reproduces it
- [/] T2 Back off 30 s when Retry-After is missing
  - ref: file:ingest/src/acme_ingest/download.py
  - verify: python -m unittest discover -s tests -t .

## Log

- 2026-10-02T08:01Z [claude-code 45e3] created
- 2026-10-04T08:22Z [claude-code 45e3] updated Context
- 2026-10-04T08:22Z [claude-code 45e3] updated Requirements
- 2026-10-04T08:22Z [claude-code 45e3] updated Acceptance criteria
- 2026-10-04T08:24Z [you] approved requirements → open
- 2026-10-04T08:26Z [claude-code 45e3] claimed (open → in-progress)
- 2026-10-04T08:28Z [claude-code 45e3] updated Plan
- 2026-10-04T08:30Z [claude-code 45e3] added T1, T2
- 2026-10-04T08:32Z [you] approved plan
- 2026-10-04T08:34Z [claude-code 45e3] started T1
- 2026-10-04T08:36Z [claude-code 45e3] T1 done: test_429_without_retry_after_waits_30s reproduces it
- 2026-10-04T08:38Z [claude-code 45e3] started T2
- 2026-10-04T08:40Z [claude-code 45e3] linked branch fix/DEMO-0020-handle-429, pr https://github.com/severinlindenmann/orch-demo-ingest/pull/1
- 2026-10-04T08:42Z [claude-code 45e3] added artifact 429-repro.log (log) for T1 for AC1
- 2026-10-04T08:44Z [claude-code 45e3] linked build https://github.com/severinlindenmann/orch-demo-ingest/pull/1/checks for T2 for AC2
- 2026-10-04T08:46Z [claude-code 45e3] CI fails on purpose for now: the reproducing test landed before the fix.
- 2026-10-04T11:05Z [claude-code 45e3] linked sprint S1
- 2026-10-04T14:21Z [claude-code 45e3] claimed
