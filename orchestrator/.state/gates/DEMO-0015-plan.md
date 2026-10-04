## Plan

1. Decide where the per-gateway streak state lives (see open question).
2. Add a streak counter keyed by gateway_id, reset on a non-breaching run.
3. Emit a log-level alert when the streak reaches 3.
4. Unit test for the 3-strikes logic.
