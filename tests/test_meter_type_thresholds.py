from __future__ import annotations

from datetime import datetime, timezone

from acme.config import PipelineConfig
from acme.models import RawMeterRead
from acme.transform import normalize_reads


def test_threshold_for_known_and_unknown_meter_types():
    config = PipelineConfig()
    assert config.threshold_for("residential") == 50.0
    assert config.threshold_for("industrial") == 1000.0
    assert config.threshold_for("unknown-type") == config.max_interval_kwh
    assert config.threshold_for(None) == config.max_interval_kwh


def test_normalize_reads_uses_per_meter_type_threshold():
    config = PipelineConfig()
    raw = [
        RawMeterRead(
            meter_id="MTR-100",
            gateway_id="GW-20",
            read_at=datetime(2026, 9, 1, tzinfo=timezone.utc),
            kwh=600.0,
            meter_type="industrial",
        ),
        RawMeterRead(
            meter_id="MTR-101",
            gateway_id="GW-20",
            read_at=datetime(2026, 9, 1, tzinfo=timezone.utc),
            kwh=60.0,
            meter_type="residential",
        ),
    ]
    normalized = normalize_reads(raw, config)
    by_id = {r.meter_id: r for r in normalized}
    assert by_id["MTR-100"].is_suspect is False
    assert by_id["MTR-101"].is_suspect is True
