from __future__ import annotations

from datetime import datetime, timezone

import pytest

from acme.config import PipelineConfig
from acme.models import RawMeterRead


@pytest.fixture
def config() -> PipelineConfig:
    return PipelineConfig()


@pytest.fixture
def raw_reads() -> list[RawMeterRead]:
    return [
        RawMeterRead(
            meter_id="MTR-001",
            gateway_id="GW-01",
            read_at=datetime(2026, 9, 1, 0, 0, tzinfo=timezone.utc),
            kwh=1.2,
        ),
        RawMeterRead(
            meter_id="MTR-001",
            gateway_id="GW-01",
            read_at=datetime(2026, 9, 1, 0, 15, tzinfo=timezone.utc),
            kwh=1.4,
        ),
        RawMeterRead(
            meter_id="MTR-002",
            gateway_id="GW-02",
            read_at=datetime(2026, 9, 1, 0, 0, tzinfo=timezone.utc),
            kwh=120.0,
        ),
    ]
