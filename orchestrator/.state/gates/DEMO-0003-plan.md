## Plan

1. Add suspect_rate_percent(report) with an explicit zero-rows guard.
2. Regression test for total_rows == 0.
3. Regression test for the normal case to lock in the percentage math.
