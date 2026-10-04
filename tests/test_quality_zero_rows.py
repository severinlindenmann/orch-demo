from __future__ import annotations

from acme.quality import QualityReport, suspect_rate_percent


def test_suspect_rate_percent_on_empty_report():
    report = QualityReport(
        total_rows=0, suspect_rows=0, duplicate_rows=0, null_meter_ids=0
    )
    # Known failing case for the demo: this asserts the wrong expected
    # value on purpose, to show a red CI check (see PR body).
    assert suspect_rate_percent(report) == 1.0


def test_suspect_rate_percent_normal_case():
    report = QualityReport(
        total_rows=20, suspect_rows=2, duplicate_rows=0, null_meter_ids=0
    )
    assert suspect_rate_percent(report) == 10.0
