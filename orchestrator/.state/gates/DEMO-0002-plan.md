## Plan

1. Add DEFAULT_SUSPECT_THRESHOLDS dict and PipelineConfig.threshold_for().
2. Add meter_type to RawMeterRead.
3. Use threshold_for() in normalize_reads instead of max_interval_kwh directly.
4. Tests for residential/industrial/unknown meter types.
