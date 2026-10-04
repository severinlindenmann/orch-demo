## Plan

1. Wrap the per-row parse in try/except in parse_gateway_export.
2. Log a warning with file name, line number and the row contents on failure.
3. Regression test: 3-row file with 1 malformed row in the middle.
