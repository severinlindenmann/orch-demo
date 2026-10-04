from __future__ import annotations

from acme.quality import build_quality_report
from acme.transform import normalize_reads


def test_quality_report_counts_suspect_rows(raw_reads, config):
    normalized = normalize_reads(raw_reads, config)
    report = build_quality_report(normalized)
    assert report.total_rows == 3
    assert report.suspect_rows == 1
    assert report.null_meter_ids == 0


def test_quality_report_passes_under_threshold(raw_reads, config):
    normalized = normalize_reads(raw_reads, config)
    report = build_quality_report(normalized)
    assert report.passed(max_suspect_rate=0.5) is True


def test_quality_report_fails_over_threshold(raw_reads, config):
    normalized = normalize_reads(raw_reads, config)
    report = build_quality_report(normalized)
    assert report.passed(max_suspect_rate=0.01) is False
