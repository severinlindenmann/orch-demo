"""Transform raw gateway reads into the canonical meter_reads fact shape."""
from __future__ import annotations

from acme.config import PipelineConfig
from acme.models import MeterRead, RawMeterRead


def normalize_reads(
    raw_reads: list[RawMeterRead], config: PipelineConfig
) -> list[MeterRead]:
    """Convert raw reads into normalized `MeterRead` rows.

    Readings above `config.max_interval_kwh` are kept but marked suspect
    rather than dropped, so quality checks downstream can decide what to
    do with them.
    """
    normalized: list[MeterRead] = []
    for raw in raw_reads:
        threshold = config.threshold_for(raw.meter_type)
        normalized.append(
            MeterRead(
                meter_id=raw.meter_id,
                read_at=raw.read_at,
                kwh=raw.kwh,
                is_suspect=raw.kwh > threshold,
                source_gateway_id=raw.gateway_id,
            )
        )
    return normalized


def dedupe_reads(reads: list[MeterRead]) -> list[MeterRead]:
    """Drop duplicate (meter_id, read_at) rows, keeping the first occurrence."""
    seen: set[tuple[str, object]] = set()
    deduped: list[MeterRead] = []
    for read in reads:
        key = (read.meter_id, read.read_at)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(read)
    return deduped
