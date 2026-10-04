## Plan

1. In _parse_timestamp / RawMeterRead construction, detect a naive datetime.
2. Attach UTC and log a warning with the gateway id.
3. Regression test for a naive-timestamp row.
