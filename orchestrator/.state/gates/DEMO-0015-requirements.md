## Requirements

- Track suspect rate history per gateway across runs.
- Emit an alert after 3 consecutive breaches of the suspect-rate threshold for the same gateway.

## Acceptance criteria

- [ ] Per-gateway suspect-rate history is tracked across runs
- [ ] An alert (log line) fires after 3 consecutive breaches
- [ ] A single bad run, or breaches from different gateways, does not alert

## Out of scope

- Routing the alert anywhere beyond a log line (paging, Slack, etc.) — follow-up ticket.
