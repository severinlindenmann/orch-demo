from __future__ import annotations

from pathlib import Path

from acme.ingest import load_gateway_exports, parse_gateway_export


def test_parse_gateway_export(tmp_path: Path):
    export = tmp_path / "gw01.csv"
    export.write_text(
        "meter_id,gateway_id,read_at,kwh\n"
        "MTR-001,GW-01,2026-09-01T00:00:00Z,1.2\n"
        "MTR-001,GW-01,2026-09-01T00:15:00Z,1.4\n"
    )
    reads = parse_gateway_export(export)
    assert len(reads) == 2
    assert reads[0].meter_id == "MTR-001"


def test_load_gateway_exports_reads_all_csvs(tmp_path: Path):
    (tmp_path / "gw01.csv").write_text(
        "meter_id,gateway_id,read_at,kwh\nMTR-001,GW-01,2026-09-01T00:00:00Z,1.0\n"
    )
    (tmp_path / "gw02.csv").write_text(
        "meter_id,gateway_id,read_at,kwh\nMTR-002,GW-02,2026-09-01T00:00:00Z,2.0\n"
    )
    reads = load_gateway_exports(tmp_path)
    assert len(reads) == 2
