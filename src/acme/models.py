"""Shared data shapes used across the ingest/transform/quality pipeline."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class RawMeterRead(BaseModel):
    """One interval read as it arrives from a substation gateway export."""

    meter_id: str
    gateway_id: str
    read_at: datetime
    kwh: float = Field(ge=0)
    meter_type: str | None = None
    quality_flag: str | None = None


class MeterRead(BaseModel):
    """A normalized meter read, ready for the fact table."""

    meter_id: str
    read_at: datetime
    kwh: float
    is_suspect: bool = False
    source_gateway_id: str
