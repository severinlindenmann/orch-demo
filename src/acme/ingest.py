"""Ingest raw interval-read exports from substation gateways."""
from __future__ import annotations

import csv
from pathlib import Path

from acme.models import RawMeterRead


def parse_gateway_export(path: Path) -> list[RawMeterRead]:
    """Parse one gateway export CSV into a list of `RawMeterRead`.

    Gateway exports are plain CSV with columns:
    `meter_id, gateway_id, read_at, kwh`.
    """
    reads: list[RawMeterRead] = []
    with path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            reads.append(
                RawMeterRead(
                    meter_id=row["meter_id"],
                    gateway_id=row["gateway_id"],
                    read_at=row["read_at"],
                    kwh=float(row["kwh"]),
                )
            )
    return reads


def load_gateway_exports(export_dir: Path) -> list[RawMeterRead]:
    """Parse every `.csv` export found directly under `export_dir`."""
    reads: list[RawMeterRead] = []
    for csv_path in sorted(export_dir.glob("*.csv")):
        reads.extend(parse_gateway_export(csv_path))
    return reads
