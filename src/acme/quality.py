"""Quality gate rules applied before publishing meter_reads to the warehouse."""
from __future__ import annotations

from dataclasses import dataclass

from acme.models import MeterRead


@dataclass
class QualityReport:
    total_rows: int
    suspect_rows: int
    duplicate_rows: int
    null_meter_ids: int

    @property
    def suspect_rate(self) -> float:
        if self.total_rows == 0:
            return 0.0
        return self.suspect_rows / self.total_rows

    def passed(self, max_suspect_rate: float = 0.05) -> bool:
        return self.null_meter_ids == 0 and self.suspect_rate <= max_suspect_rate


def suspect_rate_percent(report: QualityReport) -> float:
    """Suspect rate as a percentage, for the on-call summary line.

    Guards the zero-rows case explicitly rather than relying on the
    caller to check `total_rows` first.
    """
    if report.total_rows == 0:
        return 0.0
    return 100 * report.suspect_rows / report.total_rows


def build_quality_report(reads: list[MeterRead]) -> QualityReport:
    seen: set[tuple[str, object]] = set()
    duplicates = 0
    null_ids = 0
    suspect = 0
    for read in reads:
        if not read.meter_id:
            null_ids += 1
        key = (read.meter_id, read.read_at)
        if key in seen:
            duplicates += 1
        else:
            seen.add(key)
        if read.is_suspect:
            suspect += 1
    return QualityReport(
        total_rows=len(reads),
        suspect_rows=suspect,
        duplicate_rows=duplicates,
        null_meter_ids=null_ids,
    )
