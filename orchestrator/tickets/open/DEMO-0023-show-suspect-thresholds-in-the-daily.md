---
id: DEMO-0023
title: Show suspect thresholds in the daily report
type: feature
priority: normal
size: s
status: open
created: 2026-10-02T08:07Z
updated: 2026-10-04T11:11Z
external:
- key: GH-32
  url: https://github.com/severinlindenmann/orch-demo/issues/32
repos: []
branches: {}
worktrees: {}
prs: []
parent: null
sprint: S2
blocked_by:
- DEMO-0022
follow_ups: []
labels: []
gates:
  requirements:
    approved: 2026-10-02T21:54Z
    via: tty
    hash: sha256:bc33b11af8196732fd210717d98fccd386a9d9f5bbbea1d943f9a6b5f12d6a38
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
artifacts:
- name: daily-report-mockup.png
  kind: screenshot
  sha256: 7f94f5e479ea9db02371cf9294238ec8cd8591dadbda6f17c9bf68fb64b3b022
  size: 2039
  added: 2026-10-02T21:52Z
  label: Daily report mock-up with the threshold column
  ac: 1
---

# DEMO-0023 — Show suspect thresholds in the daily report

## Requirements

- Show the threshold that applied next to each suspect read in the daily report.
- Layout as in the mock-up:

  ![Daily report with a threshold column](artifact:daily-report-mockup.png)

## Acceptance criteria

- [ ] The report has a threshold column
- [ ] Old reports still render

## Log

- 2026-10-02T08:07Z [copilot 306b] created
- 2026-10-02T21:50Z [copilot 306b] updated Requirements
- 2026-10-02T21:50Z [copilot 306b] updated Acceptance criteria
- 2026-10-02T21:52Z [copilot 306b] added artifact daily-report-mockup.png (screenshot) for AC1
- 2026-10-02T21:54Z [you] approved requirements → open
- 2026-10-02T21:56Z [you] edited the ticket file
- 2026-10-04T11:11Z [copilot 306b] linked sprint S2
