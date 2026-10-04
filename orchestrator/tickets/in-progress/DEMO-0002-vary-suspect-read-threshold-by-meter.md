---
id: DEMO-0002
title: Vary suspect-read threshold by meter type
type: feature
priority: high
size: m
status: in-progress
created: 2026-10-02T07:43Z
updated: 2026-10-02T07:47Z
external:
- key: '3'
  url: https://github.com/severinlindenmann/orch-demo/issues/3
repos:
- acme-energy-data
branches:
  acme-energy-data: fix/DEMO-0002-suspect-threshold-by-meter-type
worktrees: {}
prs:
- repo: acme-energy-data
  url: https://github.com/severinlindenmann/orch-demo/pull/20
  state: draft
parent: null
blocked_by: []
follow_ups: []
labels: []
gates:
  requirements:
    approved: 2026-10-02T07:47Z
    via: tty
    hash: sha256:7aa6f399d656117a6bd280c26b668bc8dcbc68e53b6d22e6e41167e6f55aeacb
  plan:
    approved: 2026-10-02T07:47Z
    via: tty
    hash: sha256:d28bb51ce26930798ea18a27eb1c24f862038cbbf8275ed0f32377779c628e46
  verify:
    verdict: null
    at: null
    via: null
questions: []
claim:
  session: cc8be880-3610-520a-8cce-3b15f6753080
  harness: claude-code
  at: 2026-10-02T07:47Z
sessions:
- id: cc8be880-3610-520a-8cce-3b15f6753080
  harness: claude-code
  model: null
  started: 2026-10-02T07:47Z
---

# DEMO-0002 — Vary suspect-read threshold by meter type

## Ask

## Context

## Requirements

- Suspect-value threshold must vary by meter type (residential/commercial/industrial).
- Reads without a known meter type must keep today's single global threshold.

## Acceptance criteria

- [ ] PipelineConfig.threshold_for(meter_type) returns the right threshold per type
- [ ] Unknown or missing meter_type falls back to max_interval_kwh
- [ ] normalize_reads uses the per-type threshold instead of the global constant

## Out of scope

- Backfilling meter_type for historical reads that don't have it (separate ticket).

## Proposal

## Plan

1. Add DEFAULT_SUSPECT_THRESHOLDS dict and PipelineConfig.threshold_for().
2. Add meter_type to RawMeterRead.
3. Use threshold_for() in normalize_reads instead of max_interval_kwh directly.
4. Tests for residential/industrial/unknown meter types.

## Current state

## Verification

## Decisions

## Log

- 2026-10-02T07:43Z [claude-code cc8b] created
- 2026-10-02T07:47Z [claude-code cc8b] updated Requirements
- 2026-10-02T07:47Z [claude-code cc8b] updated Acceptance criteria
- 2026-10-02T07:47Z [claude-code cc8b] updated Out of scope
- 2026-10-02T07:47Z [claude-code cc8b] updated Plan
- 2026-10-02T07:47Z [you] approved requirements → open
- 2026-10-02T07:47Z [claude-code cc8b] claimed (open → in-progress)
- 2026-10-02T07:47Z [you] approved plan
- 2026-10-02T07:47Z [claude-code cc8b] linked branch fix/DEMO-0002-suspect-threshold-by-meter-type
- 2026-10-02T07:47Z [claude-code cc8b] linked pr https://github.com/severinlindenmann/orch-demo/pull/20
- 2026-10-02T07:47Z [claude-code cc8b] PR #20 open, CI green
- 2026-10-02T07:47Z [claude-code cc8b] Review on PR #20 requested changes: document thresholds in sql/marts, and add a test for an explicit unknown meter_type string. Picking this back up.

## Findings
