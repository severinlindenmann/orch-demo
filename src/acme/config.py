"""Pipeline configuration for the Acme Energy meter-read pipeline."""
from __future__ import annotations

from dataclasses import dataclass, field


#: Per meter-type override of the suspect-value threshold. Industrial
#: meters legitimately draw well above the residential default.
DEFAULT_SUSPECT_THRESHOLDS: dict[str, float] = {
    "residential": 50.0,
    "commercial": 150.0,
    "industrial": 1000.0,
}


@dataclass(frozen=True)
class PipelineConfig:
    """Static configuration for a single ingest run."""

    gateway_export_dir: str = "data/raw/gateway_exports"
    staging_table: str = "stg_meter_reads"
    fact_table: str = "fct_meter_reads"
    max_interval_kwh: float = 50.0
    """Readings above this threshold for a 15-minute interval are flagged as suspect.

    Used as the fallback when a read has no known meter type; see
    `suspect_thresholds` for the per meter-type overrides.
    """
    suspect_thresholds: dict[str, float] = field(
        default_factory=lambda: dict(DEFAULT_SUSPECT_THRESHOLDS)
    )
    allowed_late_days: int = 3
    """How many days late a gateway export may arrive before it is rejected outright."""

    def threshold_for(self, meter_type: str | None) -> float:
        """Suspect threshold for `meter_type`, or the global default if unknown."""
        if meter_type is None:
            return self.max_interval_kwh
        return self.suspect_thresholds.get(meter_type, self.max_interval_kwh)


DEFAULT_CONFIG = PipelineConfig()
