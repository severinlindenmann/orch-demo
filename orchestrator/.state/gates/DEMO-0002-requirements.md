## Requirements

- Suspect-value threshold must vary by meter type (residential/commercial/industrial).
- Reads without a known meter type must keep today's single global threshold.

## Acceptance criteria

- [ ] PipelineConfig.threshold_for(meter_type) returns the right threshold per type
- [ ] Unknown or missing meter_type falls back to max_interval_kwh
- [ ] normalize_reads uses the per-type threshold instead of the global constant

## Out of scope

- Backfilling meter_type for historical reads that don't have it (separate ticket).
