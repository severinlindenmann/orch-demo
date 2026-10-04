## Plan

1. Add _parse_timestamp() that tries ISO 8601 first, then the DD/MM/YYYY HH:MM format.
2. Use it for read_at before constructing RawMeterRead.
3. Regression test for a file using the alternate format.
