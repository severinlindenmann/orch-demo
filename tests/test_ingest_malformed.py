from __future__ import annotations

from pathlib import Path

from acme.ingest import parse_gateway_export


def test_parse_gateway_export_skips_malformed_rows(tmp_path: Path):
    export = tmp_path / "gw07.csv"
    export.write_text(
        "meter_id,gateway_id,read_at,kwh\n"
        "MTR-001,GW-07,2026-09-01T00:00:00Z,1.2\n"
        "MTR-002,GW-07,2026-09-01T00:00:00Z,not-a-number\n"
        "MTR-003,GW-07,2026-09-01T00:15:00Z,1.5\n"
    )
    reads = parse_gateway_export(export)
    assert len(reads) == 2
    assert [r.meter_id for r in reads] == ["MTR-001", "MTR-003"]
