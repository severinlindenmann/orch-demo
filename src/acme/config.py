"""Pipeline configuration for the Acme Energy meter-read pipeline."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PipelineConfig:
    """Static configuration for a single ingest run."""

    gateway_export_dir: str = "data/raw/gateway_exports"
    staging_table: str = "stg_meter_reads"
    fact_table: str = "fct_meter_reads"
    max_interval_kwh: float = 50.0
    """Readings above this threshold for a 15-minute interval are flagged as suspect."""
    allowed_late_days: int = 3
    """How many days late a gateway export may arrive before it is rejected outright."""


DEFAULT_CONFIG = PipelineConfig()
